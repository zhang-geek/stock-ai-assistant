"""Claude LLM Provider"""

from __future__ import annotations

from typing import AsyncIterator

import anthropic

from stock_assistant.llm.base import LLMResponse, Message

# Claude定价 (USD per 1M tokens)
PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.0},
}


class ClaudeProvider:
    provider_name = "claude"

    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.default_model = "claude-sonnet-4-20250514"

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 8192,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> LLMResponse:
        model = model or self.default_model

        # 分离system消息
        system_msg = ""
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system_msg = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        kwargs = {}
        if system_msg:
            kwargs["system"] = system_msg

        response = await self.client.messages.create(
            model=model,
            messages=chat_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        content = response.content[0].text if response.content else ""
        pricing = PRICING.get(model, PRICING["claude-sonnet-4-20250514"])
        cost = (
            response.usage.input_tokens * pricing["input"] / 1_000_000
            + response.usage.output_tokens * pricing["output"] / 1_000_000
        )

        return LLMResponse(
            content=content,
            model=model,
            provider=self.provider_name,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cost_usd=cost,
        )

    async def stream(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        model = model or self.default_model

        system_msg = ""
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system_msg = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        kwargs = {}
        if system_msg:
            kwargs["system"] = system_msg

        async with self.client.messages.stream(
            model=model,
            messages=chat_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        ) as stream:
            async for text in stream.text_stream:
                yield text
