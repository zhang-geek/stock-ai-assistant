"""舆情情感分析 - 调用 LLM 分析帖子情感"""

from __future__ import annotations

import json
import logging
from datetime import datetime, date

from stock_assistant.core.database import get_session
from stock_assistant.core.models import SentimentPost
from stock_assistant.llm.base import TaskType
from stock_assistant.llm.router import get_router

logger = logging.getLogger(__name__)

SENTIMENT_PROMPT = """\
你是一位专业的A股舆情分析师。请分析以下关于股票 {symbol} 的帖子/新闻标题的情感倾向。

帖子列表：
{posts_text}

请以 JSON 数组格式返回分析结果，每条包含：
- index: 帖子序号（从0开始）
- score: 情感分数，-1.0（极度利空）到 1.0（极度利好）
- label: 情感标签，"利好" / "利空" / "中性"

只返回 JSON 数组，不要其他内容。示例：
[{{"index": 0, "score": 0.6, "label": "利好"}}, {{"index": 1, "score": -0.3, "label": "利空"}}]
"""

SUMMARY_PROMPT = """\
你是一位专业的A股舆情分析师。请根据以下今日舆情数据，生成简洁的舆情简报。

{data}

请包含：
1. 整体情绪倾向（偏多/偏空/中性）
2. 主要观点归纳（2-3条）
3. 值得关注的风险或机会
4. 操作建议

用简洁的中文输出，控制在300字以内。
"""


class SentimentAnalyzer:
    """舆情情感分析器"""

    async def analyze_posts(
        self, posts: list[dict], symbol: str
    ) -> list[dict]:
        """用 LLM 分析帖子情感

        Args:
            posts: fetch_posts 返回的帖子列表
            symbol: 股票代码

        Returns:
            附带 sentiment_score 和 sentiment_label 的帖子列表
        """
        if not posts:
            return []

        # 拼接帖子文本
        lines = []
        for i, p in enumerate(posts):
            lines.append(f"{i}. {p['title']}")
        posts_text = "\n".join(lines)

        prompt = SENTIMENT_PROMPT.format(symbol=symbol, posts_text=posts_text)

        router = get_router()
        try:
            answer = await router.ask(
                prompt, task_type=TaskType.SENTIMENT_ANALYSIS
            )
            results = self._parse_llm_response(answer)
        except Exception as e:
            logger.warning("LLM 情感分析失败: %s", e)
            # 回退：全部标记中性
            results = [
                {"index": i, "score": 0.0, "label": "中性"}
                for i in range(len(posts))
            ]

        # 合并结果
        result_map = {r["index"]: r for r in results}
        enriched: list[dict] = []
        for i, post in enumerate(posts):
            r = result_map.get(i, {"score": 0.0, "label": "中性"})
            enriched.append({
                **post,
                "sentiment_score": r["score"],
                "sentiment_label": r["label"],
            })

        return enriched

    def _parse_llm_response(self, text: str) -> list[dict]:
        """解析 LLM 返回的 JSON 结果"""
        # 尝试提取 JSON 部分（LLM 可能包裹在 markdown 代码块中）
        text = text.strip()
        if "```" in text:
            # 提取代码块中的内容
            parts = text.split("```")
            for part in parts:
                cleaned = part.strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
                if cleaned.startswith("["):
                    text = cleaned
                    break

        # 找到第一个 [ 和最后一个 ]
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1:
            logger.warning("LLM 返回格式异常，无法解析 JSON")
            return []

        json_str = text[start : end + 1]
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning("JSON 解析失败: %s", e)
            return []

        # 验证数据结构
        results = []
        for item in data:
            if not isinstance(item, dict):
                continue
            results.append({
                "index": int(item.get("index", 0)),
                "score": float(item.get("score", 0.0)),
                "label": str(item.get("label", "中性")),
            })

        return results

    def save_to_db(
        self, posts: list[dict], symbol: str, platform: str = "eastmoney"
    ) -> int:
        """将分析结果保存到数据库

        Returns:
            保存的记录数
        """
        session = get_session()
        count = 0
        try:
            for post in posts:
                record = SentimentPost(
                    platform=platform,
                    author=post.get("author", ""),
                    content=post.get("title", ""),
                    symbol=symbol,
                    sentiment_score=post.get("sentiment_score"),
                    sentiment_label=post.get("sentiment_label"),
                    url=post.get("url", ""),
                    post_time=None,
                    created_at=datetime.now(),
                )
                session.add(record)
                count += 1
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("保存舆情数据失败: %s", e)
            raise
        finally:
            session.close()

        return count

    async def daily_summary(self, symbol: str | None = None) -> str:
        """每日舆情汇总

        Args:
            symbol: 股票代码，None 则汇总所有

        Returns:
            LLM 生成的舆情简报
        """
        session = get_session()
        try:
            query = session.query(SentimentPost).filter(
                SentimentPost.created_at >= datetime.combine(
                    date.today(), datetime.min.time()
                )
            )
            if symbol:
                query = query.filter(SentimentPost.symbol == symbol)

            records = query.all()
        finally:
            session.close()

        if not records:
            return "今日暂无舆情数据。请先运行 scan 命令抓取数据。"

        # 统计
        total = len(records)
        positive = sum(1 for r in records if (r.sentiment_score or 0) > 0.2)
        negative = sum(1 for r in records if (r.sentiment_score or 0) < -0.2)
        neutral = total - positive - negative

        # 构建数据摘要
        data_lines = [
            f"统计：共 {total} 条，利好 {positive} 条，利空 {negative} 条，中性 {neutral} 条",
            f"正面比例: {positive / total * 100:.1f}%，负面比例: {negative / total * 100:.1f}%",
            "",
            "代表性帖子：",
        ]
        # 取最正面和最负面各3条
        sorted_records = sorted(records, key=lambda r: r.sentiment_score or 0)
        for r in sorted_records[:3]:
            data_lines.append(f"  [利空 {r.sentiment_score:.1f}] {r.content}")
        for r in sorted_records[-3:]:
            data_lines.append(f"  [利好 {r.sentiment_score:.1f}] {r.content}")

        data_text = "\n".join(data_lines)
        if symbol:
            data_text = f"股票: {symbol}\n" + data_text

        prompt = SUMMARY_PROMPT.format(data=data_text)

        router = get_router()
        summary = await router.ask(prompt, task_type=TaskType.SENTIMENT_ANALYSIS)
        return summary
