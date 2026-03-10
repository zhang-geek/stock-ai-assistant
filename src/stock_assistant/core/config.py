"""配置加载模块 - 从YAML和环境变量加载配置"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"


class DatabaseConfig(BaseModel):
    url: str = f"sqlite:///{DATA_DIR / 'db' / 'stock_assistant.db'}"


class MarketConfig(BaseModel):
    default_exchange: str = "A"
    trading_hours: dict[str, list[str]] = {
        "morning": ["09:30", "11:30"],
        "afternoon": ["13:00", "15:00"],
    }


class SentimentConfig(BaseModel):
    platforms: list[str] = ["xueqiu", "eastmoney"]
    scrape_interval_minutes: int = 30
    max_posts_per_scan: int = 100


class PaperTradingConfig(BaseModel):
    initial_capital: float = 1_000_000
    max_position_pct: float = 0.10
    agents: list[str] = ["technical", "fundamental", "sentiment"]


class ReportsConfig(BaseModel):
    output_dir: str = str(DATA_DIR / "reports")
    format: str = "markdown"
    schedule: dict[str, str] = {
        "morning_brief": "08:30",
        "evening_review": "16:00",
    }


class LLMProviderConfig(BaseModel):
    model: str
    base_url: str | None = None
    max_tokens: int = 4096


class LLMConfig(BaseModel):
    task_routing: dict[str, str] = {}
    providers: dict[str, LLMProviderConfig] = {}


class Settings(BaseSettings):
    """全局配置 - 合并YAML配置和环境变量"""

    # API Keys (from .env)
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""
    openai_api_key: str = ""
    tushare_token: str = ""
    xueqiu_cookie: str = ""

    # Sub-configs (from YAML)
    database: DatabaseConfig = DatabaseConfig()
    market: MarketConfig = MarketConfig()
    sentiment: SentimentConfig = SentimentConfig()
    paper_trading: PaperTradingConfig = PaperTradingConfig()
    reports: ReportsConfig = ReportsConfig()
    llm: LLMConfig = LLMConfig()

    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "extra": "ignore"}


def _load_yaml(path: Path) -> dict[str, Any]:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def load_settings() -> Settings:
    """加载并合并所有配置"""
    settings_data = _load_yaml(CONFIG_DIR / "settings.yaml")
    llm_data = _load_yaml(CONFIG_DIR / "llm_profiles.yaml")

    # 合并LLM配置
    if llm_data:
        settings_data["llm"] = llm_data

    return Settings(**settings_data)


# 全局单例
_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings
