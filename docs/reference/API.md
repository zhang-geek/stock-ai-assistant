# API 参考文档

## 📡 FastAPI 接口文档

**API 基础地址**: `http://localhost:8000/api`

**Swagger UI**: http://localhost:8000/docs

---

## 🔍 行情接口 (`/api/quote`)

### 1. 获取实时行情

```http
GET /api/quote/realtime?symbols=000001,600000
```

**参数**:
- `symbols` (string, required): 股票代码，多个用逗号分隔

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "symbol": "000001",
      "name": "平安银行",
      "price": 10.81,
      "change_pct": 0.46,
      "open": 10.77,
      "high": 10.81,
      "low": 10.73,
      "prev_close": 10.76,
      "volume": 790112,
      "amount": 851000000,
      "turnover": 0.42
    }
  ]
}
```

### 2. 获取指数行情

```http
GET /api/quote/index
```

**响应**:
```json
{
  "code": 0,
  "data": [
    {
      "symbol": "sh000001",
      "name": "上证指数",
      "price": 3245.18,
      "change_pct": 0.52
    }
  ]
}
```

### 3. 获取日K线数据

```http
GET /api/quote/daily/{symbol}?start=2024-01-01&end=2024-12-31&adjust=qfq
```

**参数**:
- `symbol` (string, required): 股票代码
- `start` (string, optional): 开始日期
- `end` (string, optional): 结束日期
- `adjust` (string, optional): 复权类型 (qfq/hfq/none)

### 4. 涨幅榜

```http
GET /api/quote/top-gainers?limit=10
```

### 5. 跌幅榜

```http
GET /api/quote/top-losers?limit=10
```

### 6. 板块行情

```http
GET /api/quote/sectors?limit=15
```

---

## 💬 AI 问答接口 (`/api/chat`)

### 1. 提问

```http
POST /api/chat/ask
Content-Type: application/json

{
  "question": "分析今天大盘走势"
}
```

**响应**:
```json
{
  "code": 0,
  "data": "根据今日市场表现...",
  "metadata": {
    "provider": "deepseek",
    "tokens": 1234,
    "cost_usd": 0.0012
  }
}
```

### 2. 流式问答 (SSE)

```http
GET /api/chat/stream?question=分析大盘
```

**响应** (Server-Sent Events):
```
data: {"chunk": "根据"}
data: {"chunk": "今日"}
data: {"chunk": "市场"}
data: {"done": true}
```

---

## 📊 市场监控接口 (`/api/market`)

### 1. 市场概览

```http
GET /api/market/overview
```

### 2. 异动监控

```http
GET /api/market/alerts?type=volume_surge
```

**参数**:
- `type`: 异动类型 (volume_surge, price_spike, etc.)

---

## 📰 舆情分析接口 (`/api/sentiment`)

### 1. 股票舆情

```http
GET /api/sentiment/{symbol}
```

### 2. 新闻列表

```http
GET /api/sentiment/news?symbol=000001&limit=20
```

---

## 📈 回测接口 (`/api/backtest`)

### 1. 上传交易记录

```http
POST /api/backtest/upload
Content-Type: multipart/form-data

file: trades.csv
```

### 2. 获取回测统计

```http
GET /api/backtest/stats/{backtest_id}
```

### 3. 回测列表

```http
GET /api/backtest/list
```

---

## 🎯 风格探索接口 (`/api/style`)

### 1. 分析交易风格

```http
POST /api/style/analyze
Content-Type: application/json

{
  "backtest_id": 123
}
```

---

## 💼 模拟交易接口 (`/api/paper`)

### 1. 创建订单

```http
POST /api/paper/order
Content-Type: application/json

{
  "symbol": "000001",
  "action": "buy",
  "quantity": 100,
  "price": 10.50
}
```

### 2. 持仓查询

```http
GET /api/paper/positions
```

### 3. 账户信息

```http
GET /api/paper/account
```

---

## 📑 财报分析接口 (`/api/financial`)

### 1. 上传财报

```http
POST /api/financial/upload
Content-Type: multipart/form-data

file: report.pdf
symbol: 000001
```

### 2. 财报分析

```http
GET /api/financial/analyze/{report_id}
```

---

## 💰 费用统计接口 (`/api/cost`)

### 1. 费用统计

```http
GET /api/cost/stats?days=30
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "total_cost": 0.0003,
    "total_calls": 4,
    "by_provider": {
      "deepseek": {
        "calls": 4,
        "cost": 0.0003
      }
    },
    "by_task_type": {
      "general": {
        "calls": 2,
        "cost": 0.0001
      }
    }
  }
}
```

---

## ⭐ 自选股接口 (`/api/watchlist`)

### 1. 添加自选股

```http
POST /api/watchlist
Content-Type: application/json

{
  "symbol": "000001",
  "name": "平安银行"
}
```

### 2. 获取自选股列表

```http
GET /api/watchlist
```

### 3. 删除自选股

```http
DELETE /api/watchlist/{symbol}
```

---

## 🔐 认证接口 (待实现)

### 1. 登录

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "user",
  "password": "pass"
}
```

### 2. 注册

```http
POST /api/auth/register
```

---

## 📝 通用响应格式

### 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

### 错误响应

```json
{
  "code": 1001,
  "message": "参数错误",
  "detail": "symbol 参数不能为空"
}
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 数据不存在 |
| 1003 | 数据库错误 |
| 2001 | API 调用失败 |
| 2002 | 限流 |
| 3001 | 未授权 |
| 5000 | 服务器错误 |

---

## 🔧 开发工具

### Swagger UI

访问 http://localhost:8000/docs 查看交互式 API 文档

### ReDoc

访问 http://localhost:8000/redoc 查看美化的 API 文档

### 测试 API

```bash
# 使用 curl
curl http://localhost:8000/api/quote/index

# 使用 httpie
http GET http://localhost:8000/api/quote/index

# 使用 Python requests
import requests
response = requests.get('http://localhost:8000/api/quote/index')
print(response.json())
```

---

## 📚 相关文档

- [开发指南](../development/DEVELOPMENT.md)
- [部署指南](../deployment/DEPLOYMENT.md)
- [数据库模型](DATABASE.md)
