"""LLM路由器 - 根据任务类型自动选择最合适的模型"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime

from stock_assistant.core.config import get_settings
from stock_assistant.core.database import get_session
from stock_assistant.core.models import LLMUsage
from stock_assistant.llm.base import LLMResponse, Message, TaskType


class LLMRouter:
    """任务→模型路由器

    根据 llm_profiles.yaml 中的配置，将不同类型的任务路由到对应的LLM。
    同时记录每次调用的token用量和费用。
    """

    def __init__(self):
        self._providers = {}
        self._initialized = False

    def _ensure_init(self):
        if self._initialized:
            return
        settings = get_settings()
        llm_config = settings.llm

        # 初始化可用的Provider
        if settings.deepseek_api_key:
            from stock_assistant.llm.providers.deepseek import DeepSeekProvider
            base_url = "https://api.deepseek.com"
            if "deepseek" in llm_config.providers:
                base_url = llm_config.providers["deepseek"].base_url or base_url
            self._providers["deepseek"] = DeepSeekProvider(
                api_key=settings.deepseek_api_key, base_url=base_url
            )

        if settings.anthropic_api_key:
            from stock_assistant.llm.providers.claude import ClaudeProvider
            self._providers["claude"] = ClaudeProvider(api_key=settings.anthropic_api_key)

        if settings.openai_api_key:
            from stock_assistant.llm.providers.openai_provider import OpenAIProvider
            self._providers["openai"] = OpenAIProvider(api_key=settings.openai_api_key)

        self._initialized = True

    def _get_provider_for_task(self, task_type: TaskType):
        """根据任务类型获取对应的Provider"""
        self._ensure_init()
        settings = get_settings()
        routing = settings.llm.task_routing

        # 从配置获取provider名称
        provider_name = routing.get(task_type.value, "")

        # 如果配置了且可用，使用配置的provider
        if provider_name and provider_name in self._providers:
            return self._providers[provider_name]

        # 回退：按优先级尝试可用的provider
        for fallback in ["deepseek", "claude", "openai"]:
            if fallback in self._providers:
                return self._providers[fallback]

        raise RuntimeError(
            "没有可用的LLM Provider。请在 .env 文件中配置至少一个API Key:\n"
            "  DEEPSEEK_API_KEY=sk-xxx\n"
            "  ANTHROPIC_API_KEY=sk-ant-xxx\n"
            "  OPENAI_API_KEY=sk-xxx"
        )

    def _log_usage(self, response: LLMResponse, task_type: TaskType):
        """记录API用量到数据库"""
        try:
            session = get_session()
            usage = LLMUsage(
                provider=response.provider,
                model=response.model,
                task_type=task_type.value,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost_usd=response.cost_usd,
                timestamp=datetime.now(),
            )
            session.add(usage)
            session.commit()
            session.close()
        except Exception:
            pass  # 费用记录失败不应阻塞主流程

    async def complete(
        self,
        messages: list[Message],
        task_type: TaskType = TaskType.GENERAL,
        **kwargs,
    ) -> LLMResponse:
        """发送请求到对应模型"""
        provider = self._get_provider_for_task(task_type)

        # 从config获取模型特定参数
        settings = get_settings()
        provider_config = settings.llm.providers.get(provider.provider_name)
        if provider_config and "model" not in kwargs:
            kwargs.setdefault("model", provider_config.model)
            kwargs.setdefault("max_tokens", provider_config.max_tokens)

        response = await provider.complete(messages, **kwargs)
        self._log_usage(response, task_type)
        return response

    async def ask(
        self,
        question: str,
        system: str = "你是一个专业的A股投资助手。",
        task_type: TaskType = TaskType.GENERAL,
        **kwargs,
    ) -> str:
        """简化的问答接口"""
        messages = [
            Message(role="system", content=system),
            Message(role="user", content=question),
        ]
        response = await self.complete(messages, task_type=task_type, **kwargs)
        return response.content

    async def stream(
        self,
        messages: list[Message],
        task_type: TaskType = TaskType.GENERAL,
        **kwargs,
    ) -> AsyncIterator[str]:
        """流式发送请求到对应模型"""
        provider = self._get_provider_for_task(task_type)

        # 从config获取模型特定参数
        settings = get_settings()
        provider_config = settings.llm.providers.get(provider.provider_name)
        if provider_config and "model" not in kwargs:
            kwargs.setdefault("model", provider_config.model)
            kwargs.setdefault("max_tokens", provider_config.max_tokens)

        async for chunk in provider.stream(messages, **kwargs):
            yield chunk

    def get_available_providers(self) -> list[str]:
        """获取已配置的Provider列表"""
        self._ensure_init()
        return list(self._providers.keys())


# 全局单例
_router: LLMRouter | None = None


def get_router() -> LLMRouter:
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router
