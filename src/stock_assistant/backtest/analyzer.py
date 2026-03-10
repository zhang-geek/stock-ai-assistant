"""交易记录分析"""

from __future__ import annotations

from collections import defaultdict


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
            buys: dict[str, list] = defaultdict(list)
            paired: list[dict] = []

            for t in trades:
                if t.direction == "buy":
                    buys[t.symbol].append(t)
                elif t.direction == "sell" and buys[t.symbol]:
                    buy_trade = buys[t.symbol].pop(0)
                    profit_rate = (t.price - buy_trade.price) / buy_trade.price
                    paired.append({
                        "symbol": t.symbol,
                        "name": t.name or buy_trade.name,
                        "buy_price": buy_trade.price,
                        "sell_price": t.price,
                        "quantity": min(buy_trade.quantity, t.quantity),
                        "profit_rate": profit_rate,
                        "buy_time": buy_trade.trade_time,
                        "sell_time": t.trade_time,
                    })

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
                monthly[month_key] += p["profit_rate"] * p["quantity"] * p["buy_price"]

            return {
                "total_trades": total_trades,
                "paired_count": len(paired),
                "win_rate": win_rate,
                "avg_profit": avg_profit,
                "max_profit": max_profit,
                "max_loss": max_loss,
                "profit_loss_ratio": profit_loss_ratio,
                "most_traded": most_traded,
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
