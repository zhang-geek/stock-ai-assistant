"""财报分析模块单元测试"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


from stock_assistant.financial.pdf_parser import FinancialReportParser


# ========== PDF 解析器测试 ==========


class TestFinancialReportParser:
    """FinancialReportParser 测试"""

    def test_extract_key_metrics_revenue(self):
        text = "公司实现营业收入：1,234.56亿元，同比增长15.3%。"
        parser = FinancialReportParser()
        metrics = parser.extract_key_metrics(text)
        assert "营业收入" in metrics
        assert "1234.56亿元" == metrics["营业收入"]

    def test_extract_key_metrics_net_profit(self):
        text = "净利润：89.12万元"
        parser = FinancialReportParser()
        metrics = parser.extract_key_metrics(text)
        assert "净利润" in metrics
        assert "89.12万元" == metrics["净利润"]

    def test_extract_key_metrics_roe(self):
        text = "加权平均净资产收益率：18.50%"
        parser = FinancialReportParser()
        metrics = parser.extract_key_metrics(text)
        assert "ROE" in metrics
        assert "18.50%" == metrics["ROE"]

    def test_extract_key_metrics_gross_margin(self):
        text = "毛利率 32.15%，净利率 12.80%"
        parser = FinancialReportParser()
        metrics = parser.extract_key_metrics(text)
        assert metrics.get("毛利率") == "32.15%"
        assert metrics.get("净利率") == "12.80%"

    def test_extract_key_metrics_debt_ratio(self):
        text = "资产负债率：65.30%"
        parser = FinancialReportParser()
        metrics = parser.extract_key_metrics(text)
        assert metrics.get("资产负债率") == "65.30%"

    def test_extract_key_metrics_eps(self):
        text = "基本每股收益：2.35元"
        parser = FinancialReportParser()
        metrics = parser.extract_key_metrics(text)
        assert metrics.get("每股收益") == "2.35元"

    def test_extract_key_metrics_cash_flow(self):
        text = "经营活动产生的现金流量净额：-500.00万元"
        parser = FinancialReportParser()
        metrics = parser.extract_key_metrics(text)
        assert "经营活动现金流" in metrics
        assert "-500.00万元" == metrics["经营活动现金流"]

    def test_extract_key_metrics_empty_text(self):
        parser = FinancialReportParser()
        metrics = parser.extract_key_metrics("")
        assert metrics == {}

    def test_extract_key_metrics_no_match(self):
        parser = FinancialReportParser()
        metrics = parser.extract_key_metrics("这段文本不包含任何财务指标。")
        assert metrics == {}

    def test_extract_key_metrics_multiple(self):
        text = (
            "营业收入：500.00亿元\n"
            "净利润：80.00亿元\n"
            "毛利率 35.20%\n"
            "资产负债率：45.10%\n"
            "基本每股收益：3.50元\n"
        )
        parser = FinancialReportParser()
        metrics = parser.extract_key_metrics(text)
        assert len(metrics) >= 5

    def test_extract_text_with_mock_pdf(self, tmp_path):
        """使用mock测试extract_text"""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "第一页内容"

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        parser = FinancialReportParser()
        with patch("stock_assistant.financial.pdf_parser.pdfplumber.open", return_value=mock_pdf):
            text = parser.extract_text("fake.pdf")

        assert text == "第一页内容"

    def test_extract_text_max_pages(self):
        """测试 max_pages 截断"""
        pages = []
        for i in range(50):
            p = MagicMock()
            p.extract_text.return_value = f"Page {i}"
            pages.append(p)

        mock_pdf = MagicMock()
        mock_pdf.pages = pages
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        parser = FinancialReportParser()
        with patch("stock_assistant.financial.pdf_parser.pdfplumber.open", return_value=mock_pdf):
            text = parser.extract_text("fake.pdf", max_pages=5)

        # 应该只有5页内容
        assert "Page 4" in text
        assert "Page 5" not in text

    def test_extract_tables_with_mock_pdf(self):
        """测试表格提取"""
        mock_page = MagicMock()
        mock_page.extract_tables.return_value = [
            [["指标", "数值"], ["营业收入", "100亿"]],
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        parser = FinancialReportParser()
        with patch("stock_assistant.financial.pdf_parser.pdfplumber.open", return_value=mock_pdf):
            tables = parser.extract_tables("fake.pdf")

        assert len(tables) == 1
        assert tables[0][1][0] == "营业收入"


# ========== 分析器测试 (Mock LLM) ==========


class TestFinancialAnalyzer:
    """FinancialAnalyzer 测试（Mock LLM 和数据库）"""

    def test_analyze_report_calls_llm(self):
        """测试 analyze_report 完整流程"""
        from stock_assistant.financial.analyzer import FinancialAnalyzer

        analyzer = FinancialAnalyzer()

        # Mock PDF解析
        with (
            patch.object(analyzer._parser, "extract_text", return_value="营业收入：100.00亿元\n净利润：20.00亿元"),
            patch.object(analyzer._parser, "extract_key_metrics", return_value={"营业收入": "100.00亿元"}),
            patch("stock_assistant.financial.analyzer.get_router") as mock_get_router,
            patch("stock_assistant.financial.analyzer.get_session") as mock_get_session,
        ):
            mock_router = MagicMock()
            mock_router.ask = AsyncMock(return_value="这是一份很好的财报分析结果。")
            mock_get_router.return_value = mock_router

            mock_session = MagicMock()
            mock_get_session.return_value = mock_session

            result = asyncio.run(analyzer.analyze_report("fake.pdf", symbol="000001", report_date="2024-12-31"))

        assert "财报分析结果" in result
        mock_router.ask.assert_called_once()

    def test_analyze_report_empty_pdf(self):
        """测试空PDF的处理"""
        from stock_assistant.financial.analyzer import FinancialAnalyzer

        analyzer = FinancialAnalyzer()

        with patch.object(analyzer._parser, "extract_text", return_value=""):
            result = asyncio.run(analyzer.analyze_report("fake.pdf"))

        assert "无法" in result

    def test_compare_stocks_calls_llm(self):
        """测试 compare_stocks"""
        from stock_assistant.financial.analyzer import FinancialAnalyzer

        analyzer = FinancialAnalyzer()

        with (
            patch("stock_assistant.financial.analyzer.get_session") as mock_get_session,
            patch("stock_assistant.financial.analyzer.get_router") as mock_get_router,
        ):
            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
            mock_get_session.return_value = mock_session

            mock_router = MagicMock()
            mock_router.ask = AsyncMock(return_value="对比分析结果：A优于B。")
            mock_get_router.return_value = mock_router

            # Mock akshare
            with patch("stock_assistant.data.akshare_source.get_data_source") as mock_ds:
                mock_source = MagicMock()
                mock_source.get_stock_info.return_value = {"总市值": "1000亿"}
                mock_ds.return_value = mock_source

                result = asyncio.run(analyzer.compare_stocks(["000001", "000002"]))

        assert "对比" in result
        mock_router.ask.assert_called_once()
