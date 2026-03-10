# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# A股AI助手 - Claude Code 开发指南

## 环境配置

```bash
# 创建并激活虚拟环境
python -m venv .venv
source .venv/Scripts/activate   # Git Bash
# .venv\Scripts\Activate.ps1   # PowerShell

# 安装项目（含开发依赖）
pip install -e ".[dev]"

# 可选：Web界面依赖（FastAPI/Streamlit）
pip install -e ".[web]"
```

API Key 配置（至少配置一个，推荐 DeepSeek）：
```bash
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY / ANTHROPIC_API_KEY / OPENAI_API_KEY
```

## 常用命令

```bash
# 运行
python -m stock_assistant --help
python -m stock_assistant quote 000001
python -m stock_assistant ask "分析今天大盘走势"

# 测试
pytest
pytest tests/test_llm_router.py         # 单个文件
pytest -v --asyncio-mode=auto           # 异步测试

# 代码检查
ruff check .
ruff format .
```

## 架构概览

### 核心数据流

```
CLI命令 (Typer/app.py)
  → 配置加载 (config.py: settings.yaml + .env)
  ├→ 行情命令 → AKShareSource → pandas → Rich Table输出
  └→ AI命令   → LLMRouter → 选择Provider → LLMResponse → 记录llm_usage表
```

### 目录结构

```
src/stock_assistant/
├── app.py                 # CLI入口，7个已实现命令
├── core/
│   ├── config.py          # 配置单例 get_settings()，合并YAML+env
│   ├── database.py        # SQLAlchemy引擎，get_engine()/get_session()
│   └── models.py          # 10个ORM模型
├── llm/
│   ├── base.py            # LLMProvider协议 + TaskType枚举
│   ├── router.py          # 任务路由器核心：get_router().complete()
│   ├── cost_tracker.py    # API费用统计
│   └── providers/         # deepseek.py / claude.py / openai_provider.py
└── data/
    └── akshare_source.py  # A股数据，get_data_source()单例
```

### LLM路由机制

任务类型通过 `config/llm_profiles.yaml` 的 `task_routing` 路由到对应模型：
- **高频低成本任务**（情感分析、数据提取、报告生成）→ DeepSeek
- **深度推理任务**（交易教练、Agent决策、财报分析）→ Claude

`TaskType` 枚举定义在 `llm/base.py`，路由器在 `llm/router.py` 中实现自动回退（找不到已配置的Provider时按优先级尝试其他Provider）。

### 单例模式

项目中的关键单例：
- `get_settings()` → 全局配置（core/config.py）
- `get_router()` → LLM路由器（llm/router.py）
- `get_data_source()` → AKShare数据源（data/akshare_source.py）

### 数据库

SQLite 存储在 `data/db/`，10个表通过 `core/models.py` 的 SQLAlchemy ORM 定义。新功能需要的新表在此文件添加，并调用 `init_db()` 初始化。

### 运行时数据目录（gitignore）

```
data/
├── db/        # SQLite 数据库
├── cache/     # 行情数据缓存
├── reports/   # 生成的报告（Markdown）
├── imports/   # 用户导入的券商CSV
└── pdfs/      # 财报PDF文件
```

## 开发状态与并行策略

**Phase 0 基础框架已完成，Phase 1 环境配置需优先完成后再开启并行开发。**

### 并行开发计划

Phase 1（环境配置）完成后，以下模块可由多个 subagent 同时开发：

| 模块 | 目录 | 依赖 | 状态 |
|------|------|------|------|
| 市场监控 | `market/` | 无 | ⬜ |
| 舆情监控 | `sentiment/` | 无 | ⬜ |
| 交易回测 | `backtest/` | 无 | ⬜ |
| 财报分析 | `financial/` | 无 | ⬜ |
| Web前端 | `web/` (Streamlit) | 无（渐进接入） | ⬜ |
| 风格探索 | `style/` | 需要 backtest | ⬜ |
| 模拟交易 | `paper_trading/` | 需要 market+sentiment | ⬜ |

详细的 subagent 任务说明、接口约定和依赖关系见 `DEVELOPMENT.md`。

### 新模块开发规范

- LLM 调用：`get_router().complete(messages, TaskType.XXX)`
- 数据库操作：`get_session()`，模型定义在 `core/models.py`
- CLI 命令：在 `app.py` 注册新的 Typer 子命令组
- Web 页面：放在 `src/stock_assistant/web/pages/`，共享组件放 `web/components/`
- 高频任务用 `TaskType.SENTIMENT_ANALYSIS` / `REPORT_GENERATION`（路由到DeepSeek）
- 深度推理用 `TaskType.TRADING_COACH` / `FINANCIAL_ANALYSIS`（路由到Claude）
