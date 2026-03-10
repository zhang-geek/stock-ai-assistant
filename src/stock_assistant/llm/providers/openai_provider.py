"""OpenAI GPT Provider"""

from __future__ import annotations

from typing import AsyncIterator

from openai import AsyncOpenAI

from stock_assistant.llm.base import LLMResponse, Message

PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


class OpenAIProvider:
    provider_name = "openai"

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = "gpt-4o-mini"

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> LLMResponse:
        model = model or self.default_model
        kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        usage = response.usage
        pricing = PRICING.get(model, PRICING["gpt-4o-mini"])
        cost = (
            usage.prompt_tokens * pricing["input"] / 1_000_000
            + usage.completion_tokens * pricing["output"] / 1_000_000
        )

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=model,
            provider=self.provider_name,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            cost_usd=cost,
        )

    async def stream(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        model = model or self.default_model
        stream = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
