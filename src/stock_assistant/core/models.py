"""SQLAlchemy ORM 模型定义"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Trade(Base):
    """导入的历史交易记录"""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    name = Column(String(50))
    direction = Column(String(10), nullable=False)  # buy / sell
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    fee = Column(Float, default=0)
    trade_time = Column(DateTime, nullable=False)
    broker_source = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)


class SentimentPost(Base):
    """爬取的社交媒体帖子"""
    __tablename__ = "sentiment_posts"

    id = Column(Integer, primary_key=True)
    platform = Column(String(20), nullable=False)  # xueqiu / eastmoney / wechat
    author = Column(String(100))
    content = Column(Text, nullable=False)
    symbol = Column(String(10), index=True)
    sentiment_score = Column(Float)  # -1.0 to 1.0
    sentiment_label = Column(String(20))  # bullish / bearish / neutral
    url = Column(String(500))
    post_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)


class KOLOpinion(Base):
    """大V观点追踪"""
    __tablename__ = "kol_opinions"

    id = Column(Integer, primary_key=True)
    kol_name = Column(String(100), nullable=False)
    platform = Column(String(20), nullable=False)
    symbol = Column(String(10), index=True)
    opinion = Column(Text, nullable=False)
    signal = Column(String(20))  # bullish / bearish / neutral
    confidence = Column(Float)
    source_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)


class PaperPosition(Base):
    """模拟交易持仓"""
    __tablename__ = "paper_positions"

    id = Column(Integer, primary_key=True)
    strategy_name = Column(String(50), nullable=False)
    symbol = Column(String(10), nullable=False)
    name = Column(String(50))
    direction = Column(String(10), default="long")
    entry_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    current_price = Column(Float)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime)
    exit_price = Column(Float)
    pnl = Column(Float)
    status = Column(String(20), default="open")  # open / closed


class PaperTransaction(Base):
    """模拟交易流水"""
    __tablename__ = "paper_transactions"

    id = Column(Integer, primary_key=True)
    strategy_name = Column(String(50), nullable=False)
    symbol = Column(String(10), nullable=False)
    action = Column(String(10), nullable=False)  # buy / sell
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    reasoning = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)


class DailyReport(Base):
    """生成的报告"""
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True)
    report_type = Column(String(50), nullable=False)  # morning / evening / sentiment / etc
    date = Column(String(10), nullable=False)
    content_md = Column(Text, nullable=False)
    metadata_json = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class Watchlist(Base):
    """自选股"""
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, unique=True)
    name = Column(String(50))
    sector = Column(String(50))
    notes = Column(Text)
    added_at = Column(DateTime, default=datetime.now)


class FinancialMetric(Base):
    """提取的财报指标"""
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    report_date = Column(String(10), nullable=False)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float)
    unit = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)


class LLMUsage(Base):
    """API费用追踪"""
    __tablename__ = "llm_usage"

    id = Column(Integer, primary_key=True)
    provider = Column(String(20), nullable=False)
    model = Column(String(50), nullable=False)
    task_type = Column(String(50))
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0)
    timestamp = Column(DateTime, default=datetime.now)


class MarketSignal(Base):
    """市场异动信号"""
    __tablename__ = "market_signals"

    id = Column(Integer, primary_key=True)
    signal_type = Column(String(50), nullable=False)  # volume_spike / price_limit / sector_rotation
    symbol = Column(String(10), index=True)
    description = Column(Text, nullable=False)
    severity = Column(String(20))  # low / medium / high
    detected_at = Column(DateTime, default=datetime.now)


class MarketSnapshot(Base):
    """全市场快照缓存"""
    __tablename__ = "market_snapshots"

    id = Column(Integer, primary_key=True)
    snapshot_type = Column(String(50), nullable=False, index=True)  # spot_all / sectors / index
    data_json = Column(Text, nullable=False)
    row_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class DailyBar(Base):
    """日K线缓存"""
    __tablename__ = "daily_bars"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    amount = Column(Float)
    change_pct = Column(Float)
    turnover = Column(Float)
    adjust = Column(String(10), default="qfq")  # qfq / hfq / ""
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("symbol", "date", "adjust", name="uix_daily_bar"),
    )
