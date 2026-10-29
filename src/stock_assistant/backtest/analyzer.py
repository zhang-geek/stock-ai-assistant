"""交易记录分析"""

from __future__ import annotations

from collections import defaultdict, deque


from stock_assistant.core.database import get_session
from stock_assistant.core.models import Trade
from stock_assistant.llm.base import TaskType
from stock_assistant.llm.router import get_router


class TradeAnalyzer:
    """分析历史交易记录"""

    def get_statistics(self) -> dict:
        """计算交易统计指标"""
        session = get_session()
        try:
            trades = session.query(Trade).order_by(Trade.trade_time).all()
            if not trades:
                return {"total_trades": 0}

            total_trades = len(trades)

            # 按股票分组配对买卖
            buys: dict[str, deque] = defaultdict(deque)
            paired: list[dict] = []

            for t in trades:
                if t.direction == "buy":
                    # Keep the remaining quantity in each FIFO lot.  A sell can
                    # consume only part of a lot, so the lot must stay queued.
                    buys[t.symbol].append({"trade": t, "remaining": t.quantity})
                elif t.direction == "sell":
                    remaining_sell = t.quantity
                    sell_fee_per_share = (t.fee or 0) / t.quantity if t.quantity else 0
                    while remaining_sell > 0 and buys[t.symbol]:
                        lot = buys[t.symbol][0]
                        buy_trade = lot["trade"]
                        quantity = min(lot["remaining"], remaining_sell)
                        buy_fee = (buy_trade.fee or 0) * quantity / buy_trade.quantity
                        sell_fee = sell_fee_per_share * quantity
                        gross_pnl = (t.price - buy_trade.price) * quantity
                        net_pnl = gross_pnl - buy_fee - sell_fee
                        cost_basis = buy_trade.price * quantity + buy_fee
                        profit_rate = net_pnl / cost_basis if cost_basis else 0
                        paired.append({
                            "symbol": t.symbol,
                            "name": t.name or buy_trade.name,
                            "buy_price": buy_trade.price,
                            "sell_price": t.price,
                            "quantity": quantity,
                            "profit": net_pnl,
                            "profit_rate": profit_rate,
                            "buy_time": buy_trade.trade_time,
                            "sell_time": t.trade_time,
                        })
                        lot["remaining"] -= quantity
                        remaining_sell -= quantity
                        if lot["remaining"] == 0:
                            buys[t.symbol].popleft()

            # 统计指标
            if paired:
                wins = [p for p in paired if p["profit_rate"] > 0]
                losses = [p for p in paired if p["profit_rate"] <= 0]
                profit_rates = [p["profit_rate"] for p in paired]

                win_rate = len(wins) / len(paired) if paired else 0
                avg_profit = sum(profit_rates) / len(profit_rates)
                max_profit = max(profit_rates)
                max_loss = min(profit_rates)

                avg_win = (sum(p["profit_rate"] for p in wins) / len(wins)) if wins else 0
                avg_loss = abs(sum(p["profit_rate"] for p in losses) / len(losses)) if losses else 1
                profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else float("inf")
            else:
                win_rate = avg_profit = max_profit = max_loss = profit_loss_ratio = 0

            # 交易最多的股票
            symbol_counts = defaultdict(int)
            for t in trades:
                symbol_counts[f"{t.symbol} {t.name or ''}".strip()] += 1
            most_traded = max(symbol_counts, key=symbol_counts.get) if symbol_counts else ""

            # 按月统计盈亏
            monthly: dict[str, float] = defaultdict(float)
            for p in paired:
                month_key = p["sell_time"].strftime("%Y-%m")
                monthly[month_key] += p["profit"]

            return {
                "total_trades": total_trades,
                "paired_count": len(paired),
                "win_rate": win_rate,
                "avg_profit": avg_profit,
                "max_profit": max_profit,
                "max_loss": max_loss,
                "profit_loss_ratio": profit_loss_ratio,
                "most_traded": most_traded,
                "realized_pnl": sum(p["profit"] for p in paired),
                "monthly_pnl": dict(sorted(monthly.items())),
            }
        finally:
            session.close()

    async def ai_analysis(self, stats: dict) -> str:
        """用LLM分析交易模式"""
        if stats.get("total_trades", 0) == 0:
            return "暂无交易记录，无法分析。"

        text_parts = [
            f"总交易次数: {stats['total_trades']}",
            f"配对交易数: {stats['paired_count']}",
            f"胜率: {stats['win_rate']:.1%}",
            f"平均盈利率: {stats['avg_profit']:.2%}",
            f"最大单笔盈利: {stats['max_profit']:.2%}",
            f"最大单笔亏损: {stats['max_loss']:.2%}",
            f"盈亏比: {stats['profit_loss_ratio']:.2f}",
            f"交易最多的股票: {stats['most_traded']}",
        ]
        if stats.get("monthly_pnl"):
            text_parts.append("按月盈亏(元):")
            for month, pnl in stats["monthly_pnl"].items():
                text_parts.append(f"  {month}: {pnl:+,.0f}")

        stats_text = "\n".join(text_parts)

        prompt = (
            f"以下是一位A股投资者的交易统计数据:\n\n{stats_text}\n\n"
            "请分析这位投资者的:\n"
            "1. 交易风格（短线/波段/长线）\n"
            "2. 优点和不足\n"
            "3. 具体的改进建议\n"
            "请简洁专业地回答。"
        )

        router = get_router()
        return await router.ask(prompt, task_type=TaskType.TRADING_COACH)
