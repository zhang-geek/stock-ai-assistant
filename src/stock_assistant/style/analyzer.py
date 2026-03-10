"""交易风格分析"""

from __future__ import annotations

from collections import defaultdict

from stock_assistant.core.database import get_session
from stock_assistant.core.models import Trade
from stock_assistant.llm.base import TaskType
from stock_assistant.llm.router import get_router


class StyleAnalyzer:
    """分析交易者的交易风格"""

    def analyze_style(self) -> dict:
        """分析交易风格，返回风格特征字典"""
        session = get_session()
        try:
            trades = session.query(Trade).order_by(Trade.trade_time).all()
            if not trades:
                return {}

            # FIFO 配对买卖（与 TradeAnalyzer 逻辑一致）
            buys: dict[str, list] = defaultdict(list)
            paired: list[dict] = []

            for t in trades:
                if t.direction == "buy":
                    buys[t.symbol].append(t)
                elif t.direction == "sell" and buys[t.symbol]:
                    buy_trade = buys[t.symbol].pop(0)
                    holding_days = (t.trade_time - buy_trade.trade_time).days
                    paired.append({
                        "symbol": t.symbol,
                        "name": t.name or buy_trade.name,
                        "holding_days": holding_days,
                        "buy_time": buy_trade.trade_time,
                        "sell_time": t.trade_time,
                    })

            # 平均持仓天数
            if paired:
                avg_holding_days = sum(p["holding_days"] for p in paired) / len(paired)
            else:
                avg_holding_days = 0

            # 月均交易次数
            trade_times = [t.trade_time for t in trades]
            first_trade = min(trade_times)
            last_trade = max(trade_times)
            span_days = (last_trade - first_trade).days or 1
            span_months = max(span_days / 30, 1)
            trading_frequency = len(trades) / span_months

            # 交易时间偏好
            hour_counts: dict[str, int] = defaultdict(int)
            for t in trades:
                hour = t.trade_time.hour
                if hour < 10 or (hour == 10 and t.trade_time.minute == 0):
                    hour_counts["早盘(9:30-10:00)"] += 1
                elif hour < 11 or (hour == 11 and t.trade_time.minute <= 30):
                    hour_counts["上午盘(10:00-11:30)"] += 1
                elif hour < 14:
                    hour_counts["午后盘(13:00-14:00)"] += 1
                else:
                    hour_counts["尾盘(14:00-15:00)"] += 1
            time_pattern = max(hour_counts, key=hour_counts.get) if hour_counts else "未知"

            # 持仓集中度（交易过的不同股票数量）
            unique_symbols = set(t.symbol for t in trades)
            concentration = len(unique_symbols)

            # 偏好股票（按交易次数排序 Top 5）
            symbol_counts: dict[str, int] = defaultdict(int)
            symbol_names: dict[str, str] = {}
            for t in trades:
                symbol_counts[t.symbol] += 1
                if t.name:
                    symbol_names[t.symbol] = t.name
            top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            position_preference = [
                f"{symbol_names.get(s, s)}({s}) {c}次" for s, c in top_symbols
            ]

            # 风格标签
            if avg_holding_days < 5:
                style_label = "短线炒手"
            elif avg_holding_days < 30:
                style_label = "波段操作"
            else:
                style_label = "中长线投资"

            return {
                "avg_holding_days": round(avg_holding_days, 1),
                "trading_frequency": round(trading_frequency, 1),
                "position_preference": position_preference,
                "time_pattern": time_pattern,
                "concentration": concentration,
                "style_label": style_label,
                "paired_count": len(paired),
                "total_trades": len(trades),
            }
        finally:
            session.close()

    async def ai_coach(self, style_data: dict, stats: dict) -> str:
        """AI交易教练，综合风格和统计数据给出建议"""
        if not style_data or stats.get("total_trades", 0) == 0:
            return "暂无足够的交易数据，无法提供教练建议。"

        # 构建风格描述
        style_parts = [
            f"风格标签: {style_data['style_label']}",
            f"平均持仓天数: {style_data['avg_holding_days']}天",
            f"月均交易次数: {style_data['trading_frequency']}次",
            f"交易时间偏好: {style_data['time_pattern']}",
            f"交易过的股票数: {style_data['concentration']}只",
            f"偏好股票: {', '.join(style_data['position_preference'])}",
        ]

        # 构建统计描述
        stats_parts = [
            f"总交易次数: {stats['total_trades']}",
            f"配对交易数: {stats['paired_count']}",
            f"胜率: {stats['win_rate']:.1%}",
            f"平均盈利率: {stats['avg_profit']:.2%}",
            f"最大单笔盈利: {stats['max_profit']:.2%}",
            f"最大单笔亏损: {stats['max_loss']:.2%}",
            f"盈亏比: {stats['profit_loss_ratio']:.2f}",
        ]

        style_text = "\n".join(style_parts)
        stats_text = "\n".join(stats_parts)

        prompt = (
            "作为一位资深A股交易教练，请分析以下交易者的风格和数据，并给出专业建议。\n\n"
            f"【交易风格特征】\n{style_text}\n\n"
            f"【交易统计数据】\n{stats_text}\n\n"
            "请从以下5个方面详细分析：\n"
            "1. 风格定位：这位交易者属于什么类型？\n"
            "2. 优势分析：哪些方面做得好？\n"
            "3. 弱点诊断：哪些方面需要改进？\n"
            "4. 个性化改进建议：具体可操作的建议\n"
            "5. 推荐学习方向：适合学习什么交易理论或方法？\n"
            "请简洁专业地回答。"
        )

        router = get_router()
        return await router.ask(prompt, task_type=TaskType.TRADING_COACH)
