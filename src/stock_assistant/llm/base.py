"""LLM抽象层 - 定义Provider协议和任务类型"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Protocol


class TaskType(Enum):
    """任务类型 - 决定使用哪个模型"""
    SENTIMENT_ANALYSIS = "sentiment_analysis"     # 高频，用便宜模型
    DATA_EXTRACTION = "data_extraction"           # 结构化提取，便宜模型
    REPORT_GENERATION = "report_generation"       # 报告生成
    TRADING_COACH = "trading_coach"               # 交易教练，需强推理
    AGENT_REASONING = "agent_reasoning"           # 多Agent决策
    FINANCIAL_ANALYSIS = "financial_analysis"     # 财报分析，需长上下文
    GENERAL = "general"                           # 通用对话


@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class Message:
    role: str  # system / user / assistant
    content: str


class LLMProvider(Protocol):
    """LLM提供者协议"""
    provider_name: str

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> LLMResponse: ...

    async def stream(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]: ...
