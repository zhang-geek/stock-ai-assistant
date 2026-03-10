# 数据库模型参考

## 📊 SQLAlchemy ORM 模型

**数据库**: SQLite
**位置**: `data/db/stock_assistant.db`
**ORM**: SQLAlchemy 2.0

---

## 📋 表结构

### 1. LLM 使用记录 (`llm_usage`)

记录所有 LLM API 调用的详细信息。

```python
class LLMUsage(Base):
    __tablename__ = "llm_usage"

    id: int                    # 主键
    provider: str              # 提供商 (deepseek/claude/openai)
    model: str                 # 模型名称
    task_type: str             # 任务类型
    prompt_tokens: int         # 输入 tokens
    completion_tokens: int     # 输出 tokens
    total_tokens: int          # 总 tokens
    cost_usd: float           # 费用 (美元)
    created_at: datetime       # 创建时间
```

**索引**:
- `idx_provider`: provider
- `idx_created_at`: created_at

**查询示例**:
```python
# 获取最近 30 天的费用统计
from datetime import datetime, timedelta
from sqlalchemy import func

thirty_days_ago = datetime.now() - timedelta(days=30)
total_cost = session.query(func.sum(LLMUsage.cost_usd))\
    .filter(LLMUsage.created_at >= thirty_days_ago)\
    .scalar()
```

---

### 2. 交易记录 (`trades`)

存储用户的交易记录。

```python
class Trade(Base):
    __tablename__ = "trades"

    id: int                    # 主键
    symbol: str                # 股票代码
    name: str                  # 股票名称
    action: str                # 操作 (buy/sell)
    quantity: int              # 数量
    price: float               # 价格
    amount: float              # 金额
    commission: float          # 手续费
    trade_date: date           # 交易日期
    broker: str                # 券商
    account: str               # 账户
    notes: str                 # 备注
    created_at: datetime       # 创建时间
```

**索引**:
- `idx_symbol`: symbol
- `idx_trade_date`: trade_date

---

### 3. 回测结果 (`backtest_results`)

存储回测分析结果。

```python
class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id: int                    # 主键
    name: str                  # 回测名称
    start_date: date           # 开始日期
    end_date: date             # 结束日期
    initial_capital: float     # 初始资金
    final_capital: float       # 最终资金
    total_return: float        # 总收益率
    annual_return: float       # 年化收益率
    max_drawdown: float        # 最大回撤
    sharpe_ratio: float        # 夏普比率
    win_rate: float            # 胜率
    total_trades: int          # 总交易次数
    created_at: datetime       # 创建时间
```

---

### 4. 交易风格 (`trading_styles`)

存储交易风格分析结果。

```python
class TradingStyle(Base):
    __tablename__ = "trading_styles"

    id: int                    # 主键
    backtest_id: int           # 关联回测ID
    style_type: str            # 风格类型
    confidence: float          # 置信度
    characteristics: str       # 特征描述 (JSON)
    recommendations: str       # 建议 (JSON)
    created_at: datetime       # 创建时间
```

**关系**:
```python
backtest = relationship("BacktestResult", back_populates="styles")
```

---

### 5. 模拟交易订单 (`paper_orders`)

模拟交易订单记录。

```python
class PaperOrder(Base):
    __tablename__ = "paper_orders"

    id: int                    # 主键
    symbol: str                # 股票代码
    name: str                  # 股票名称
    action: str                # 操作 (buy/sell)
    quantity: int              # 数量
    price: float               # 价格
    status: str                # 状态 (pending/filled/cancelled)
    filled_quantity: int       # 成交数量
    filled_price: float        # 成交价格
    order_time: datetime       # 下单时间
    filled_time: datetime      # 成交时间
    notes: str                 # 备注
```

**索引**:
- `idx_status`: status
- `idx_order_time`: order_time

---

### 6. 模拟持仓 (`paper_positions`)

模拟交易持仓。

```python
class PaperPosition(Base):
    __tablename__ = "paper_positions"

    id: int                    # 主键
    symbol: str                # 股票代码
    name: str                  # 股票名称
    quantity: int              # 持仓数量
    avg_cost: float            # 平均成本
    current_price: float       # 当前价格
    market_value: float        # 市值
    profit_loss: float         # 盈亏
    profit_loss_pct: float     # 盈亏比例
    updated_at: datetime       # 更新时间
```

**索引**:
- `idx_symbol`: symbol (unique)

---

### 7. 模拟账户 (`paper_accounts`)

模拟交易账户。

```python
class PaperAccount(Base):
    __tablename__ = "paper_accounts"

    id: int                    # 主键
    user_id: int               # 用户ID
    cash: float                # 现金
    market_value: float        # 持仓市值
    total_assets: float        # 总资产
    initial_capital: float     # 初始资金
    total_profit_loss: float   # 总盈亏
    total_profit_loss_pct: float # 总盈亏比例
    updated_at: datetime       # 更新时间
```

---

### 8. 财报记录 (`financial_reports`)

财报文件记录。

```python
class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id: int                    # 主键
    symbol: str                # 股票代码
    name: str                  # 股票名称
    report_type: str           # 报告类型 (annual/quarterly)
    report_period: str         # 报告期间
    file_path: str             # 文件路径
    file_size: int             # 文件大小
    analysis: str              # 分析结果 (JSON)
    uploaded_at: datetime      # 上传时间
```

---

### 9. 市场快照 (`market_snapshots`)

市场数据快照（缓存）。

```python
class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id: int                    # 主键
    snapshot_type: str         # 快照类型 (index/gainers/losers/sectors)
    data: str                  # 数据 (JSON)
    created_at: datetime       # 创建时间
    expires_at: datetime       # 过期时间
```

**索引**:
- `idx_snapshot_type`: snapshot_type
- `idx_expires_at`: expires_at

---

### 10. 日K线数据 (`daily_bars`)

日K线历史数据（缓存）。

```python
class DailyBar(Base):
    __tablename__ = "daily_bars"

    id: int                    # 主键
    symbol: str                # 股票代码
    trade_date: date           # 交易日期
    open: float                # 开盘价
    high: float                # 最高价
    low: float                 # 最低价
    close: float               # 收盘价
    volume: int                # 成交量
    amount: float              # 成交额
    adjust_type: str           # 复权类型
    created_at: datetime       # 创建时间
```

**索引**:
- `idx_symbol_date`: (symbol, trade_date) - unique
- `idx_trade_date`: trade_date

---

## 🔧 数据库操作

### 初始化数据库

```python
from stock_assistant.core.database import init_db

init_db()
```

### 获取 Session

```python
from stock_assistant.core.database import get_session

with get_session() as session:
    # 执行数据库操作
    trades = session.query(Trade).all()
```

### 添加记录

```python
from stock_assistant.core.models import Trade
from stock_assistant.core.database import get_session

trade = Trade(
    symbol="000001",
    name="平安银行",
    action="buy",
    quantity=100,
    price=10.50,
    amount=1050.00,
    trade_date=date.today()
)

with get_session() as session:
    session.add(trade)
    session.commit()
```

### 查询记录

```python
# 查询所有交易
trades = session.query(Trade).all()

# 条件查询
trades = session.query(Trade)\
    .filter(Trade.symbol == "000001")\
    .filter(Trade.action == "buy")\
    .all()

# 排序
trades = session.query(Trade)\
    .order_by(Trade.trade_date.desc())\
    .limit(10)\
    .all()

# 聚合查询
from sqlalchemy import func

total_amount = session.query(func.sum(Trade.amount))\
    .filter(Trade.action == "buy")\
    .scalar()
```

### 更新记录

```python
trade = session.query(Trade).filter(Trade.id == 1).first()
trade.notes = "已更新"
session.commit()
```

### 删除记录

```python
trade = session.query(Trade).filter(Trade.id == 1).first()
session.delete(trade)
session.commit()
```

---

## 📊 数据库迁移

### 使用 Alembic (推荐)

```bash
# 初始化 Alembic
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Add new column"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 手动迁移

```python
from sqlalchemy import text
from stock_assistant.core.database import get_engine

engine = get_engine()

with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE trades
        ADD COLUMN new_field VARCHAR(100)
    """))
    conn.commit()
```

---

## 🔍 性能优化

### 1. 批量插入

```python
trades = [
    Trade(symbol="000001", ...),
    Trade(symbol="000002", ...),
    # ...
]

session.bulk_save_objects(trades)
session.commit()
```

### 2. 延迟加载

```python
# 使用 joinedload 避免 N+1 查询
from sqlalchemy.orm import joinedload

backtests = session.query(BacktestResult)\
    .options(joinedload(BacktestResult.styles))\
    .all()
```

### 3. 索引优化

```python
# 在模型中定义索引
class Trade(Base):
    __tablename__ = "trades"

    # ...

    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'trade_date'),
    )
```

---

## 📚 相关文档

- [API 参考](API.md)
- [开发指南](../development/DEVELOPMENT.md)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
