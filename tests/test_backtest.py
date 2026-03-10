"""交易回测模块测试"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from stock_assistant.core.models import Base, Trade


@pytest.fixture()
def db_session(monkeypatch):
    """使用内存SQLite数据库"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    # 猴补丁，让 importer / analyzer 使用测试数据库
    import stock_assistant.core.database as db_mod
    monkeypatch.setattr(db_mod, "get_session", factory)

    import stock_assistant.backtest.importer as imp_mod
    monkeypatch.setattr(imp_mod, "get_session", factory)

    import stock_assistant.backtest.analyzer as ana_mod
    monkeypatch.setattr(ana_mod, "get_session", factory)

    return factory


@pytest.fixture()
def sample_csv():
    """创建测试用CSV文件"""
    content = (
        "股票代码,股票名称,买卖方向,成交价格,成交数量,手续费,成交时间\n"
        "000001,平安银行,买入,10.50,1000,5.25,2024-01-15 10:30:00\n"
        "000001,平安银行,卖出,11.20,1000,5.60,2024-02-20 14:00:00\n"
        "600519,贵州茅台,买入,1680.00,100,8.40,2024-03-01 09:45:00\n"
        "600519,贵州茅台,卖出,1650.00,100,8.25,2024-03-15 14:30:00\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


class TestTradeImporter:
    def test_import_csv(self, db_session, sample_csv):
        from stock_assistant.backtest.importer import TradeImporter

        importer = TradeImporter()
        count = importer.import_csv(sample_csv, broker="generic")

        assert count == 4

        # 验证数据库内容
        session = db_session()
        trades = session.query(Trade).all()
        assert len(trades) == 4

        buy = trades[0]
        assert buy.symbol == "000001"
        assert buy.direction == "buy"
        assert buy.price == 10.50
        assert buy.quantity == 1000
        assert buy.amount == 10500.0
        assert buy.fee == 5.25
        session.close()

    def test_import_gbk_csv(self, db_session):
        """测试GBK编码CSV"""
        from stock_assistant.backtest.importer import TradeImporter

        content = (
            "股票代码,股票名称,买卖方向,成交价格,成交数量,手续费,成交时间\n"
            "000002,万科A,买入,8.50,500,4.25,2024-05-01 10:00:00\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="gbk"
        ) as f:
            f.write(content)
            path = f.name

        try:
            importer = TradeImporter()
            count = importer.import_csv(path)
            assert count == 1
        finally:
            os.unlink(path)

    def test_import_unsupported_broker(self, db_session, sample_csv):
        from stock_assistant.backtest.importer import TradeImporter

        importer = TradeImporter()
        with pytest.raises(ValueError, match="不支持的券商格式"):
            importer.import_csv(sample_csv, broker="unknown")


class TestTradeAnalyzer:
    def _insert_trades(self, session_factory):
        """插入测试交易数据"""
        session = session_factory()
        trades = [
            Trade(
                symbol="000001", name="平安银行", direction="buy",
                price=10.50, quantity=1000, amount=10500,
                fee=5.25, trade_time=datetime(2024, 1, 15, 10, 30),
            ),
            Trade(
                symbol="000001", name="平安银行", direction="sell",
                price=11.20, quantity=1000, amount=11200,
                fee=5.60, trade_time=datetime(2024, 2, 20, 14, 0),
            ),
            Trade(
                symbol="600519", name="贵州茅台", direction="buy",
                price=1680.00, quantity=100, amount=168000,
                fee=8.40, trade_time=datetime(2024, 3, 1, 9, 45),
            ),
            Trade(
                symbol="600519", name="贵州茅台", direction="sell",
                price=1650.00, quantity=100, amount=165000,
                fee=8.25, trade_time=datetime(2024, 3, 15, 14, 30),
            ),
        ]
        session.add_all(trades)
        session.commit()
        session.close()

    def test_get_statistics(self, db_session):
        from stock_assistant.backtest.analyzer import TradeAnalyzer

        self._insert_trades(db_session)
        analyzer = TradeAnalyzer()
        stats = analyzer.get_statistics()

        assert stats["total_trades"] == 4
        assert stats["paired_count"] == 2
        # 1 win (平安银行 +6.67%), 1 loss (茅台 -1.79%) → 50%
        assert stats["win_rate"] == pytest.approx(0.5)
        assert stats["max_profit"] == pytest.approx((11.20 - 10.50) / 10.50)
        assert stats["max_loss"] == pytest.approx((1650 - 1680) / 1680)
        assert stats["profit_loss_ratio"] > 0
        assert "000001" in stats["most_traded"]

    def test_empty_statistics(self, db_session):
        from stock_assistant.backtest.analyzer import TradeAnalyzer

        analyzer = TradeAnalyzer()
        stats = analyzer.get_statistics()
        assert stats["total_trades"] == 0
