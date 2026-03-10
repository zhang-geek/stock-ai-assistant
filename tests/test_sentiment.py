"""舆情模块测试"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from stock_assistant.sentiment.analyzer import SentimentAnalyzer


# ── SentimentAnalyzer._parse_llm_response 测试 ──


class TestParseLLMResponse:
    """测试 LLM 返回结果解析"""

    def setup_method(self):
        self.analyzer = SentimentAnalyzer()

    def test_parse_valid_json(self):
        text = '[{"index": 0, "score": 0.8, "label": "利好"}, {"index": 1, "score": -0.5, "label": "利空"}]'
        result = self.analyzer._parse_llm_response(text)
        assert len(result) == 2
        assert result[0]["score"] == 0.8
        assert result[0]["label"] == "利好"
        assert result[1]["score"] == -0.5
        assert result[1]["label"] == "利空"

    def test_parse_json_in_markdown_code_block(self):
        text = '```json\n[{"index": 0, "score": 0.3, "label": "中性"}]\n```'
        result = self.analyzer._parse_llm_response(text)
        assert len(result) == 1
        assert result[0]["score"] == 0.3

    def test_parse_json_with_extra_text(self):
        text = '分析结果如下：\n[{"index": 0, "score": -0.7, "label": "利空"}]\n以上是分析。'
        result = self.analyzer._parse_llm_response(text)
        assert len(result) == 1
        assert result[0]["label"] == "利空"

    def test_parse_empty_response(self):
        result = self.analyzer._parse_llm_response("")
        assert result == []

    def test_parse_invalid_json(self):
        result = self.analyzer._parse_llm_response("这不是JSON")
        assert result == []

    def test_parse_missing_fields(self):
        text = '[{"index": 0}]'
        result = self.analyzer._parse_llm_response(text)
        assert len(result) == 1
        assert result[0]["score"] == 0.0
        assert result[0]["label"] == "中性"


# ── SentimentAnalyzer.analyze_posts 测试 ──


class TestAnalyzePosts:
    """测试情感分析流程"""

    def setup_method(self):
        self.analyzer = SentimentAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_empty_posts(self):
        result = await self.analyzer.analyze_posts([], "000001")
        assert result == []

    @pytest.mark.asyncio
    async def test_analyze_posts_with_llm(self):
        posts = [
            {"title": "利好消息", "author": "张三", "url": "", "time": ""},
            {"title": "业绩暴雷", "author": "李四", "url": "", "time": ""},
        ]

        llm_response = json.dumps([
            {"index": 0, "score": 0.8, "label": "利好"},
            {"index": 1, "score": -0.9, "label": "利空"},
        ])

        with patch("stock_assistant.sentiment.analyzer.get_router") as mock_router:
            router = MagicMock()
            router.ask = AsyncMock(return_value=llm_response)
            mock_router.return_value = router

            result = await self.analyzer.analyze_posts(posts, "000001")

        assert len(result) == 2
        assert result[0]["sentiment_score"] == 0.8
        assert result[0]["sentiment_label"] == "利好"
        assert result[1]["sentiment_score"] == -0.9

    @pytest.mark.asyncio
    async def test_analyze_posts_llm_failure_fallback(self):
        """LLM 调用失败时回退到中性"""
        posts = [
            {"title": "测试帖子", "author": "test", "url": "", "time": ""},
        ]

        with patch("stock_assistant.sentiment.analyzer.get_router") as mock_router:
            router = MagicMock()
            router.ask = AsyncMock(side_effect=RuntimeError("LLM不可用"))
            mock_router.return_value = router

            result = await self.analyzer.analyze_posts(posts, "000001")

        assert len(result) == 1
        assert result[0]["sentiment_score"] == 0.0
        assert result[0]["sentiment_label"] == "中性"


# ── EastMoneyScraper 测试 ──


class TestEastMoneyScraper:
    """测试东方财富爬虫的 HTML 解析"""

    def test_parse_posts_empty_html(self):
        from stock_assistant.sentiment.scraper import EastMoneyScraper

        scraper = EastMoneyScraper()
        result = scraper._parse_posts("<html><body></body></html>", 10)
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_posts_network_error(self):
        """网络错误应返回空列表"""
        from stock_assistant.sentiment.scraper import EastMoneyScraper

        scraper = EastMoneyScraper()
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(
                side_effect=httpx.TimeoutException("timeout")
            )
            mock_client_cls.return_value = mock_client

            result = await scraper.fetch_posts("000001")
            assert result == []


# ── AKShareNewsScraper 测试 ──


class TestAKShareNewsScraper:

    def test_fetch_posts_with_mock_data(self):
        import pandas as pd
        from stock_assistant.sentiment.scraper import AKShareNewsScraper

        mock_df = pd.DataFrame({
            "新闻标题": ["利好消息来了", "市场震荡"],
            "新闻链接": ["https://example.com/1", "https://example.com/2"],
            "文章来源": ["东财", "同花顺"],
            "发布时间": ["2024-01-01 10:00", "2024-01-01 11:00"],
        })

        scraper = AKShareNewsScraper()
        with patch("stock_assistant.data.akshare_source.get_data_source") as mock_ds:
            ds = MagicMock()
            ds.get_news.return_value = mock_df
            mock_ds.return_value = ds

            result = scraper.fetch_posts("000001")

        assert len(result) == 2
        assert result[0]["title"] == "利好消息来了"
        assert result[1]["author"] == "同花顺"
