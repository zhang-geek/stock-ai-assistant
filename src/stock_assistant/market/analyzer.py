"""市场监控核心逻辑 - 盘前简报、盘后复盘、异动扫描"""

from __future__ import annotations

from datetime import datetime

from stock_assistant.data.akshare_source import get_data_source
from stock_assistant.llm.router import get_router
from stock_assistant.llm.base import TaskType
from stock_assistant.core.database import get_session
from stock_assistant.core.models import MarketSignal


class MarketAnalyzer:
    """市场分析器，提供每日简报、复盘和异动扫描功能"""

    def __init__(self):
        self._ds = get_data_source()

    async def morning_brief(self) -> str:
        """盘前简报：获取主要指数 + 板块排行 + LLM 生成简报"""
        # 1. 获取指数数据
        index_df = self._ds.get_index_quote()
        index_text = "\n".join(
            f"  {row['name']}: {row['price']:.2f} ({row['change_pct']:+.2f}%)"
            for _, row in index_df.iterrows()
        )

        # 2. 获取板块涨跌 top 10
        sector_df = self._ds.get_sector_performance()
        sector_df = sector_df.sort_values("change_pct", ascending=False)
        top_sectors = sector_df.head(10)
        bottom_sectors = sector_df.tail(5)

        sector_up_text = "\n".join(
            f"  {row['sector']}: {row['change_pct']:+.2f}% (涨{int(row['up_count'])}家/跌{int(row['down_count'])}家)"
            for _, row in top_sectors.iterrows()
        )
        sector_down_text = "\n".join(
            f"  {row['sector']}: {row['change_pct']:+.2f}%"
            for _, row in bottom_sectors.iterrows()
        )

        # 3. 组装 prompt，让 LLM 生成盘前简报
        prompt = f"""请根据以下A股市场数据，生成一段简洁的盘前简报（300字以内）。
包含：市场整体走势判断、热点板块点评、今日关注要点。

【主要指数】
{index_text}

【涨幅前10板块】
{sector_up_text}

【跌幅后5板块】
{sector_down_text}

请用专业但易懂的语言，直接输出简报内容。"""

        router = get_router()
        return await router.ask(prompt, task_type=TaskType.REPORT_GENERATION)

    async def evening_review(self) -> str:
        """盘后复盘：今日行情总结 + 涨跌榜 + LLM 总结"""
        # 1. 获取指数数据
        index_df = self._ds.get_index_quote()
        index_text = "\n".join(
            f"  {row['name']}: {row['price']:.2f} ({row['change_pct']:+.2f}%)"
            for _, row in index_df.iterrows()
        )

        # 2. 获取涨幅榜 top 10 + 跌幅榜 top 10
        gainers = self._ds.get_top_gainers(10)
        losers = self._ds.get_top_losers(10)

        gainers_text = "\n".join(
            f"  {row['name']}({row['symbol']}): {row['price']:.2f} {row['change_pct']:+.2f}% 换手{row['turnover']:.1f}%"
            for _, row in gainers.iterrows()
        )
        losers_text = "\n".join(
            f"  {row['name']}({row['symbol']}): {row['price']:.2f} {row['change_pct']:+.2f}%"
            for _, row in losers.iterrows()
        )

        # 3. 获取板块数据
        sector_df = self._ds.get_sector_performance()
        sector_df = sector_df.sort_values("change_pct", ascending=False)
        top_sectors = sector_df.head(10)
        sector_text = "\n".join(
            f"  {row['sector']}: {row['change_pct']:+.2f}%"
            for _, row in top_sectors.iterrows()
        )

        # 4. 组装 prompt，让 LLM 生成复盘报告
        prompt = f"""请根据以下A股今日行情数据，生成一份盘后复盘报告（500字以内）。
包含：大盘走势总结、板块轮动分析、涨跌停分析、明日展望。

【主要指数】
{index_text}

【涨幅榜 TOP 10】
{gainers_text}

【跌幅榜 TOP 10】
{losers_text}

【热门板块 TOP 10】
{sector_text}

请用专业但易懂的语言，直接输出复盘报告。"""

        router = get_router()
        return await router.ask(prompt, task_type=TaskType.REPORT_GENERATION)

    async def scan_signals(self, threshold: float = 5.0) -> list[dict]:
        """异动扫描：找出涨跌幅超过阈值的股票，写入数据库

        Args:
            threshold: 涨跌幅阈值（百分比），默认5%

        Returns:
            检测到的信号列表
        """
        # 1. 获取涨幅榜和跌幅榜（取足够多的数据）
        gainers = self._ds.get_top_gainers(50)
        losers = self._ds.get_top_losers(50)

        signals = []

        # 2. 筛选涨幅超过阈值的个股
        big_gainers = gainers[gainers["change_pct"] >= threshold]
        for _, row in big_gainers.iterrows():
            signals.append({
                "signal_type": "price_surge",
                "symbol": str(row["symbol"]),
                "name": str(row["name"]),
                "change_pct": float(row["change_pct"]),
                "description": f"{row['name']}({row['symbol']}) 大涨 {row['change_pct']:+.2f}%",
                "severity": "high" if row["change_pct"] >= 9.5 else "medium",
            })

        # 3. 筛选跌幅超过阈值的个股
        big_losers = losers[losers["change_pct"] <= -threshold]
        for _, row in big_losers.iterrows():
            signals.append({
                "signal_type": "price_drop",
                "symbol": str(row["symbol"]),
                "name": str(row["name"]),
                "change_pct": float(row["change_pct"]),
                "description": f"{row['name']}({row['symbol']}) 大跌 {row['change_pct']:+.2f}%",
                "severity": "high" if row["change_pct"] <= -9.5 else "medium",
            })

        # 4. 写入 MarketSignal 表
        if signals:
            session = get_session()
            try:
                for sig in signals:
                    record = MarketSignal(
                        signal_type=sig["signal_type"],
                        symbol=sig["symbol"],
                        description=sig["description"],
                        severity=sig["severity"],
                        detected_at=datetime.now(),
                    )
                    session.add(record)
                session.commit()
            finally:
                session.close()

        return signals
