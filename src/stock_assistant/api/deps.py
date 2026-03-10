"""FastAPI 共享依赖"""

from stock_assistant.data.akshare_source import AKShareSource, get_data_source
from stock_assistant.llm.router import LLMRouter, get_router


def get_ds() -> AKShareSource:
    return get_data_source()


def get_llm() -> LLMRouter:
    return get_router()
