# A股AI辅助炒股系统 - 开发文档

## 项目概述

一个全面的AI辅助炒股系统，利用多个大模型（Claude/DeepSeek/GPT混用）帮助提升A股投资决策质量。

### 六大模块
| 模块 | 功能 | 状态 |
|------|------|------|
| 舆情监控 | 雪球/股吧/公众号爬取 + LLM情感分析 | ⬜ 待开发 |
| 交易回测 | 导入券商交易记录 + LLM分析交易模式 | ⬜ 待开发 |
| 风格探索 | 交易风格分类 + AI交易教练 | ⬜ 待开发 |
| 模拟交易 | 多Agent协作决策（技术/基本面/情绪/风控） | ⬜ 待开发 |
| 市场监控 | 盘前简报/盘后复盘/异动扫描 | ⬜ 待开发 |
| 财报分析 | PDF解析 + LLM估值分析 | ⬜ 待开发 |

---

## 技术选型

| 类别 | 选择 | 原因 |
|------|------|------|
| 语言 | Python 3.11+ | 金融/数据生态最成熟 |
| CLI框架 | Typer + Rich | 美观的命令行界面 |
| 数据源 | AKShare | 免费、无需注册、覆盖A股全数据 |
| 数据库 | SQLite (SQLAlchemy) | 单人使用足够，零配置 |
| LLM (高频) | DeepSeek | 便宜(~0.14$/M tokens)，中文好 |
| LLM (推理) | Claude Sonnet | 强推理能力，用于教练/Agent |
| 技术指标 | ta库 | 纯Python，无C依赖，Windows友好 |
| 回测 | backtrader | 简单易用，适合分析历史交易 |
| 爬虫 | httpx + beautifulsoup4 | 异步HTTP + HTML解析 |
| 财报 | pdfplumber | PDF解析 |

### LLM路由策略
不同任务自动路由到最合适的模型：
- **高频/低成本任务** → DeepSeek：情感分析、数据提取、报告生成
- **深度推理任务** → Claude：交易教练、Agent决策、财报分析
- 可在 `config/llm_profiles.yaml` 自由覆盖

---

## 项目结构

```
stock_personal/
├── pyproject.toml                 # 项目配置和依赖
├── .env.example                   # API Key模板
├── .env                           # 实际的API Key（不提交git）
├── config/
│   ├── settings.yaml              # 主配置
│   ├── llm_profiles.yaml          # LLM模型路由配置
│   └── watchlist.yaml             # 自选股列表
├── src/stock_assistant/
│   ├── app.py                     # CLI入口 (Typer)
│   ├── __main__.py                # python -m stock_assistant 支持
│   ├── core/
│   │   ├── config.py              # 配置加载 (pydantic-settings + YAML)
│   │   ├── database.py            # SQLAlchemy引擎和会话管理
│   │   └── models.py              # 10个ORM模型（交易/舆情/持仓等）
│   ├── llm/
│   │   ├── base.py                # LLMProvider协议 + TaskType枚举
│   │   ├── router.py              # 任务→模型路由器（核心）
│   │   ├── cost_tracker.py        # API费用追踪
│   │   └── providers/
│   │       ├── deepseek.py        # DeepSeek (OpenAI兼容API)
│   │       ├── claude.py          # Anthropic Claude
│   │       └── openai_provider.py # OpenAI GPT
│   ├── data/
│   │   └── akshare_source.py      # AKShare封装（行情/板块/指数/新闻）
│   ├── sentiment/                 # 模块1 - 待实现
│   ├── backtest/                  # 模块2 - 待实现
│   ├── style/                     # 模块3 - 待实现
│   ├── paper_trading/             # 模块4 - 待实现
│   ├── market/                    # 模块5 - 待实现
│   ├── financial/                 # 模块6 - 待实现
│   └── reports/                   # 报告系统 - 待实现
├── data/                          # 运行时数据（gitignore）
│   ├── db/                        # SQLite数据库
│   ├── cache/                     # 数据缓存
│   ├── reports/                   # 生成的报告
│   ├── imports/                   # 用户导入的交易CSV
│   └── pdfs/                      # 财报PDF
├── tests/                         # 测试
└── scripts/                       # 工具脚本
```

---

## 开发计划

> **并行开发策略**：Phase 0（环境配置）必须顺序完成。之后各业务模块之间相互独立，可通过多个 subagent 并行开发，大幅提升效率。Web 前端可在任何业务模块完成后同步接入，无需等待所有后端完成。

---

### ✅ Phase 0：基础框架（代码已完成）

已完成的文件：

| 文件 | 说明 | 状态 |
|------|------|------|
| `pyproject.toml` | 项目配置、所有依赖声明 | ✅ 完成 |
| `.env.example` | API Key配置模板 | ✅ 完成 |
| `.gitignore` | Git忽略规则 | ✅ 完成 |
| `config/settings.yaml` | 主配置文件 | ✅ 完成 |
| `config/llm_profiles.yaml` | LLM路由配置 | ✅ 完成 |
| `config/watchlist.yaml` | 自选股配置 | ✅ 完成 |
| `src/stock_assistant/core/config.py` | 配置加载器 | ✅ 完成 |
| `src/stock_assistant/core/database.py` | 数据库引擎 | ✅ 完成 |
| `src/stock_assistant/core/models.py` | 10个ORM模型 | ✅ 完成 |
| `src/stock_assistant/llm/base.py` | LLM抽象协议 | ✅ 完成 |
| `src/stock_assistant/llm/router.py` | 任务路由器 | ✅ 完成 |
| `src/stock_assistant/llm/cost_tracker.py` | 费用追踪 | ✅ 完成 |
| `src/stock_assistant/llm/providers/deepseek.py` | DeepSeek Provider | ✅ 完成 |
| `src/stock_assistant/llm/providers/claude.py` | Claude Provider | ✅ 完成 |
| `src/stock_assistant/llm/providers/openai_provider.py` | OpenAI Provider | ✅ 完成 |
| `src/stock_assistant/data/akshare_source.py` | AKShare数据源 | ✅ 完成 |
| `src/stock_assistant/app.py` | CLI入口（7个命令） | ✅ 完成 |

---

### ✅ Phase 1：环境配置与验证（已完成）

> 此阶段是后续所有开发的前提，必须顺序完成后再启动并行开发。

**任务清单（按顺序执行）：**

1. **安装 Python 3.11+**（如尚未安装）
   ```bash
   # 验证版本
   python --version   # 需要 >= 3.11
   ```

2. **创建虚拟环境并安装依赖**
   ```bash
   cd D:\development\projects\stock_personal
   python -m venv .venv
   source .venv/Scripts/activate      # Git Bash
   pip install -e ".[dev]"
   pip install -e ".[web]"            # 同时安装 Web 依赖备用
   ```

3. **配置 API Key**
   ```bash
   cp .env.example .env
   # 编辑 .env，至少填入 DEEPSEEK_API_KEY（推荐，性价比最高）
   ```

4. **验证安装**
   ```bash
   # 无需 API Key 的命令（验证基础功能）
   python -m stock_assistant --help
   python -m stock_assistant quote 000001
   python -m stock_assistant index
   python -m stock_assistant top up -n 5

   # 需要 API Key 的命令（验证 LLM 集成）
   python -m stock_assistant ask "今天大盘怎么样？"
   python -m stock_assistant cost
   ```

5. **运行现有测试**
   ```bash
   pytest -v
   ```

**完成标准**：以上所有命令执行成功，无报错。

---

### 🚀 Phase 2：并行开发阶段

> Phase 1 完成后，以下模块可分配给多个 subagent **同时开发**。每个模块独立成包，互不依赖。

```
Phase 1 完成
    │
    ├── [Subagent A] Phase 2A：市场监控模块
    ├── [Subagent B] Phase 2B：舆情监控模块
    ├── [Subagent C] Phase 2C：交易回测模块
    ├── [Subagent D] Phase 2D：财报分析模块
    └── [Subagent E] Phase 2E：Web 前端框架（Streamlit）
```

#### ✅ Phase 2A：市场监控（`market/`）

**Subagent 任务说明**：实现 `stock-assistant market` 命令组

| 子命令 | 功能 | 实现要点 |
|--------|------|---------|
| `market morning` | 盘前简报 | 获取昨日收盘数据 + AKShare指数 + LLM生成摘要（DeepSeek） |
| `market review` | 盘后复盘 | 今日涨跌分析 + 板块轮动 + LLM总结 |
| `market scan` | 实时异动扫描 | 扫描涨跌幅>5%个股 + 写入 `market_signals` 表 |

**接口约定**：
- 写入数据库使用 `get_session()`
- LLM 调用使用 `get_router().complete(messages, TaskType.REPORT_GENERATION)`
- 异动信号写入 `MarketSignal` ORM 模型
- 在 `app.py` 注册 `market` 子命令组

---

#### ✅ Phase 2B：舆情监控（`sentiment/`）

**Subagent 任务说明**：实现 `stock-assistant sentiment` 命令组

| 子命令 | 功能 | 实现要点 |
|--------|------|---------|
| `sentiment scan <symbol>` | 扫描个股舆情 | httpx爬取东方财富股吧 + LLM情感评分（DeepSeek） |
| `sentiment daily` | 每日舆情汇总 | 聚合watchlist所有股票情感 + 生成报告 |
| `sentiment kol` | 大V观点追踪 | 抓取特定账号内容 + 写入 `kol_opinions` 表 |

**接口约定**：
- 爬虫使用 `httpx` + `BeautifulSoup4`
- 情感分析使用 `TaskType.SENTIMENT_ANALYSIS`（路由到DeepSeek）
- 结果写入 `SentimentPost` 和 `KolOpinion` ORM 模型

---

#### ✅ Phase 2C：交易回测（`backtest/`）

**Subagent 任务说明**：实现 `stock-assistant import` 和 `stock-assistant backtest` 命令组

| 子命令 | 功能 | 实现要点 |
|--------|------|---------|
| `import trades <csv>` | 导入券商交易记录 | 解析CSV → 写入 `trades` 表（支持常见券商格式） |
| `backtest analyze` | 分析历史交易 | 胜率/盈亏比/最大回撤 + LLM总结（Claude） |
| `backtest replay` | 回放交易策略 | 用 backtrader 对历史交易进行可视化回测 |

**接口约定**：
- CSV解析用 pandas
- 统计计算用 numpy/pandas
- LLM分析使用 `TaskType.DATA_EXTRACTION` 提取模式，`TaskType.TRADING_COACH` 生成建议

---

#### ✅ Phase 2D：财报分析（`financial/`）

**Subagent 任务说明**：实现 `stock-assistant financial` 命令组

| 子命令 | 功能 | 实现要点 |
|--------|------|---------|
| `financial analyze <pdf>` | 分析财报PDF | pdfplumber解析 → 提取关键指标 → LLM估值分析（Claude长上下文） |
| `financial compare <symbols>` | 同行对比 | 从AKShare获取财务数据 + LLM对比分析 |

**接口约定**：
- PDF文件放在 `data/pdfs/`
- 解析结果写入 `FinancialMetric` ORM 模型
- LLM分析使用 `TaskType.FINANCIAL_ANALYSIS`（路由到Claude）

---

#### ✅ Phase 2E：Web 前端（Streamlit）

**Subagent 任务说明**：搭建 `src/stock_assistant/web/` Streamlit 应用

**可与 2A-2D 并行开始**——先实现已有 Phase 0 功能的 Web 界面，后续接入各业务模块。

| 页面 | 功能 | 数据来源 |
|------|------|---------|
| `🏠 首页` | 主要指数 + 自选股概览 | AKShareSource |
| `📊 行情` | 个股查询 + K线图 | AKShareSource |
| `💬 AI问答` | 多轮对话界面 | LLMRouter |
| `💰 API费用` | 费用统计图表 | cost_tracker |
| `📈 市场监控` | 异动信号 + 市场简报 | Phase 2A 完成后接入 |
| `🔍 舆情` | 个股情感趋势 | Phase 2B 完成后接入 |
| `📋 交易记录` | 历史交易 + 回测结果 | Phase 2C 完成后接入 |

**技术约定**：
- 入口文件：`src/stock_assistant/web/app.py`
- 启动命令：`streamlit run src/stock_assistant/web/app.py`
- 各页面放在 `src/stock_assistant/web/pages/` 目录
- 共享组件（图表、表格样式）放在 `src/stock_assistant/web/components/`
- 直接调用现有 `get_data_source()`、`get_router()`、`get_session()` 单例

---

### Phase 3：有依赖的模块（Phase 2 部分完成后）

以下模块依赖 Phase 2 的数据基础，待对应模块完成后开发：

#### ✅ Phase 3A：风格探索（`style/`）
**依赖**：Phase 2C 交易回测数据
- `style analyze`：分析历史交易的风格（短线/波段/长线，持仓天数、频率、集中度）
- `style coach`：AI教练给出改进建议（使用 `TaskType.TRADING_COACH` → Claude）

#### ✅ Phase 3B：模拟交易（`paper_trading/`）
**依赖**：Phase 2A 市场监控 + Phase 2B 舆情监控
- 多Agent协作决策：技术面Agent + 基本面Agent + 情绪面Agent + 风控Agent
- `paper portfolio`：查看模拟投资组合
- `paper buy/sell`：手动模拟交易
- `paper decide`：AI多Agent协作决策
- `paper history`：查看交易历史
- 结果写入 `PaperPosition` 和 `PaperTransaction` ORM 模型

---

### 开发进度总览

```
Phase 0  基础框架          ✅ 完成
Phase 1  环境配置与验证     ✅ 完成
         │
         ▼（Phase 1 完成后并行启动）
         ├─ Phase 2A  市场监控        ✅ 完成
         ├─ Phase 2B  舆情监控        ✅ 完成
         ├─ Phase 2C  交易回测        ✅ 完成
         ├─ Phase 2D  财报分析        ✅ 完成
         └─ Phase 2E  Web前端         ✅ 完成
                   │
                   ▼（2C完成后）    ▼（2A+2B完成后）
              Phase 3A 风格探索     Phase 3B 模拟交易
                   ✅                    ✅
```

---

## 环境配置指南

### 1. 安装Python
需要 Python 3.11+。推荐从 https://www.python.org/downloads/ 安装。

安装时请确保勾选 **"Add Python to PATH"**。

### 2. 创建虚拟环境并安装
```bash
cd D:\development\projects\stock_personal

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows PowerShell)
.venv\Scripts\Activate.ps1

# 或 (Windows CMD)
.venv\Scripts\activate.bat

# 或 (Git Bash)
source .venv/Scripts/activate

# 安装项目及依赖
pip install -e ".[dev]"
```

### 3. 配置API Key
```bash
# 方式1：运行配置向导
python -m stock_assistant setup

# 方式2：手动创建 .env 文件
cp .env.example .env
# 然后编辑 .env 填入你的API Key
```

**API Key获取方式**：
| Provider | 获取地址 | 价格 |
|----------|---------|------|
| DeepSeek（推荐） | https://platform.deepseek.com/ | ~0.14$/百万token |
| Anthropic Claude | https://console.anthropic.com/ | ~3$/百万token |
| OpenAI | https://platform.openai.com/ | ~0.15$/百万token (mini) |

建议**至少配置DeepSeek**，性价比最高，中文能力强。

### 4. 测试运行
```bash
# 查看帮助
python -m stock_assistant --help

# 查看行情（不需要API Key）
python -m stock_assistant quote 000001

# 查看指数
python -m stock_assistant index

# AI问答（需要API Key）
python -m stock_assistant ask "分析一下今天的大盘走势"
```

---

## CLI命令参考

```
stock-assistant
├── setup                              # 首次配置引导
├── quote <symbol>                     # 查询实时行情
├── ask <question>                     # 向AI提问
├── index                              # 查看主要指数
├── top [up|down] -n 10                # 涨跌幅排行
├── sectors -n 20                      # 板块排行
├── cost -d 30                         # API费用统计
│
│  === 以下命令待后续Phase实现 ===
├── market morning|review|scan         # 市场监控
├── sentiment scan|daily|kol           # 舆情监控
├── import trades <file>               # 导入交易记录
├── backtest analyze|replay            # 回测分析
├── style analyze|coach                # 风格探索
├── paper run|portfolio|history        # 模拟交易
├── financial analyze <pdf>            # 财报分析
└── report generate|schedule           # 报告管理
```

---

## 数据库模型

共10个表，使用SQLAlchemy ORM定义在 `core/models.py`：

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `trades` | 导入的历史交易 | symbol, direction, price, quantity, trade_time |
| `sentiment_posts` | 爬取的社交帖子 | platform, content, sentiment_score |
| `kol_opinions` | 大V观点 | kol_name, opinion, signal |
| `paper_positions` | 模拟持仓 | strategy_name, symbol, entry_price, pnl |
| `paper_transactions` | 模拟交易流水 | action, price, reasoning |
| `daily_reports` | 生成的报告 | report_type, content_md |
| `watchlist` | 自选股 | symbol, name, sector |
| `financial_metrics` | 财报指标 | metric_name, value |
| `llm_usage` | API费用 | provider, model, cost_usd |
| `market_signals` | 市场异动 | signal_type, description |
