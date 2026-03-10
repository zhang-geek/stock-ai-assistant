# A股AI助手 - 启动指南

## 后端启动 (FastAPI)

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 初始化数据库
python -c "from stock_assistant.core.database import init_db; init_db()"

# 启动 FastAPI 服务器
uvicorn stock_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档: http://localhost:8000/docs

## 前端启动 (React + Vite)

```bash
cd frontend
npm run dev
```

访问前端: http://localhost:5173

## 架构说明

### 后端 API (FastAPI)

- **端口**: 8000
- **API 前缀**: `/api`
- **Swagger UI**: http://localhost:8000/docs
- **10 个路由模块**:
  - `/api/quote` - 行情数据
  - `/api/market` - 市场监控
  - `/api/sentiment` - 舆情分析
  - `/api/backtest` - 交易回测
  - `/api/style` - 风格探索
  - `/api/paper` - 模拟交易
  - `/api/financial` - 财报分析
  - `/api/chat` - AI问答 (支持SSE流式)
  - `/api/cost` - 费用统计
  - `/api/watchlist` - 自选股

### 前端 (React + TypeScript + Ant Design)

- **端口**: 5173
- **技术栈**: React 18 + TypeScript + Vite + Ant Design 5
- **10 个页面**:
  - `/` - 首页 (指数、涨跌榜、板块)
  - `/quote` - 行情查询
  - `/chat` - AI问答
  - `/market` - 市场监控
  - `/sentiment` - 舆情分析
  - `/backtest` - 交易回测
  - `/style` - 风格探索
  - `/paper` - 模拟交易
  - `/financial` - 财报分析
  - `/cost` - 费用统计

### 数据缓存

三级缓存架构:
1. **内存缓存** (60-300秒 TTL)
2. **数据库缓存** (1小时 TTL, MarketSnapshot + DailyBar 表)
3. **AKShare API** (最终数据源)

日K线支持增量更新，只拉取最新数据。

## 开发命令

```bash
# 代码检查
ruff check src/

# 运行测试
pytest tests/ -v

# CLI 命令 (原有功能保留)
python -m stock_assistant quote 000001
python -m stock_assistant ask "分析大盘走势"
```
