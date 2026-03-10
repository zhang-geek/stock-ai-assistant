"""市场监控模块测试"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from stock_assistant.market.analyzer import MarketAnalyzer


def _make_index_df():
    """构造模拟指数数据"""
    return pd.DataFrame([
        {"symbol": "000001", "name": "上证指数", "price": 3200.0, "change_pct": 0.5, "amount": 3e11},
        {"symbol": "399001", "name": "深证成指", "price": 11000.0, "change_pct": 0.8, "amount": 4e11},
    ])


def _make_sector_df():
    """构造模拟板块数据"""
    rows = []
    for i in range(15):
        rows.append({
            "sector": f"板块{i}",
            "code": f"BK{i:04d}",
            "price": 1000 + i,
            "change_pct": 5.0 - i * 0.8,
            "market_cap": 1e12,
            "turnover": 2.0,
            "up_count": 30 - i,
            "down_count": 10 + i,
        })
    return pd.DataFrame(rows)


def _make_gainers_df():
    """构造模拟涨幅榜"""
    return pd.DataFrame([
        {"symbol": "000001", "name": "测试股A", "price": 10.0, "change_pct": 10.0, "amount": 1e9, "turnover": 15.0},
        {"symbol": "000002", "name": "测试股B", "price": 20.0, "change_pct": 6.5, "amount": 2e9, "turnover": 8.0},
        {"symbol": "000003", "name": "测试股C", "price": 5.0, "change_pct": 3.0, "amount": 5e8, "turnover": 4.0},
    ])


def _make_losers_df():
    """构造模拟跌幅榜"""
    return pd.DataFrame([
        {"symbol": "600001", "name": "测试股X", "price": 8.0, "change_pct": -9.8, "amount": 1e9, "turnover": 12.0},
        {"symbol": "600002", "name": "测试股Y", "price": 15.0, "change_pct": -6.0, "amount": 8e8, "turnover": 5.0},
        {"symbol": "600003", "name": "测试股Z", "price": 30.0, "change_pct": -2.0, "amount": 3e8, "turnover": 2.0},
    ])


class TestMarketAnalyzerInit:
    """测试 MarketAnalyzer 实例化"""

    @patch("stock_assistant.market.analyzer.get_data_source")
    def test_can_instantiate(self, mock_ds):
        analyzer = MarketAnalyzer()
        assert analyzer is not None
        assert analyzer._ds is mock_ds.return_value


class TestMorningBrief:
    """测试盘前简报"""

    @pytest.mark.asyncio
    @patch("stock_assistant.market.analyzer.get_router")
    @patch("stock_assistant.market.analyzer.get_data_source")
    async def test_morning_brief(self, mock_ds, mock_router):
        # 准备 mock
        ds = mock_ds.return_value
        ds.get_index_quote.return_value = _make_index_df()
        ds.get_sector_performance.return_value = _make_sector_df()

        router = mock_router.return_value
        router.ask = AsyncMock(return_value="今日市场整体震荡上行...")

        # 执行
        analyzer = MarketAnalyzer()
        result = await analyzer.morning_brief()

        # 验证
        assert result == "今日市场整体震荡上行..."
        ds.get_index_quote.assert_called_once()
        ds.get_sector_performance.assert_called_once()
        router.ask.assert_called_once()
        # 验证传入了正确的 task_type
        call_kwargs = router.ask.call_args
        from stock_assistant.llm.base import TaskType
        assert call_kwargs.kwargs["task_type"] == TaskType.REPORT_GENERATION


class TestScanSignals:
    """测试异动扫描"""

    @pytest.mark.asyncio
    @patch("stock_assistant.market.analyzer.get_session")
    @patch("stock_assistant.market.analyzer.get_data_source")
    async def test_scan_finds_signals(self, mock_ds, mock_session):
        # 准备 mock
        ds = mock_ds.return_value
        ds.get_top_gainers.return_value = _make_gainers_df()
        ds.get_top_losers.return_value = _make_losers_df()

        session = MagicMock()
        mock_session.return_value = session

        # 执行 (阈值 5%)
        analyzer = MarketAnalyzer()
        signals = await analyzer.scan_signals(threshold=5.0)

        # 验证：应该有 10%, 6.5% 的涨和 -9.8%, -6.0% 的跌 = 4 个信号
        assert len(signals) == 4

        # 验证涨停信号
        surge_signals = [s for s in signals if s["signal_type"] == "price_surge"]
        assert len(surge_signals) == 2
        assert surge_signals[0]["severity"] == "high"  # 10% >= 9.5
        assert surge_signals[1]["severity"] == "medium"  # 6.5% < 9.5

        # 验证跌停信号
        drop_signals = [s for s in signals if s["signal_type"] == "price_drop"]
        assert len(drop_signals) == 2
        assert drop_signals[0]["severity"] == "high"  # -9.8% <= -9.5

        # 验证写入数据库
        assert session.add.call_count == 4
        session.commit.assert_called_once()
        session.close.assert_called_once()

    @pytest.mark.asyncio
    @patch("stock_assistant.market.analyzer.get_session")
    @patch("stock_assistant.market.analyzer.get_data_source")
    async def test_scan_no_signals(self, mock_ds, mock_session):
        """阈值很高时没有信号"""
        ds = mock_ds.return_value
        ds.get_top_gainers.return_value = _make_gainers_df()
        ds.get_top_losers.return_value = _make_losers_df()

        analyzer = MarketAnalyzer()
        signals = await analyzer.scan_signals(threshold=20.0)

        assert len(signals) == 0
        # 没有信号时不应该打开数据库会话
        mock_session.assert_not_called()
