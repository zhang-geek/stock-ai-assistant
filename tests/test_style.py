"""风格探索模块测试"""

from __future__ import annotations

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

    import stock_assistant.core.database as db_mod
    monkeypatch.setattr(db_mod, "get_session", factory)

    import stock_assistant.style.analyzer as style_mod
    monkeypatch.setattr(style_mod, "get_session", factory)

    return factory


class TestStyleAnalyzer:
    def test_instantiate(self):
        """测试 StyleAnalyzer 可以实例化"""
        from stock_assistant.style.analyzer import StyleAnalyzer

        analyzer = StyleAnalyzer()
        assert analyzer is not None

    def test_empty_data(self, db_session):
        """测试无交易数据时返回空结果"""
        from stock_assistant.style.analyzer import StyleAnalyzer

        analyzer = StyleAnalyzer()
        result = analyzer.analyze_style()
        assert result == {}

    def test_short_term_style(self, db_session):
        """测试短线风格判断（持仓 < 5天）"""
        from stock_assistant.style.analyzer import StyleAnalyzer

        session = db_session()
        trades = [
            Trade(
                symbol="000001", name="平安银行", direction="buy",
                price=10.50, quantity=1000, amount=10500,
                fee=5.25, trade_time=datetime(2024, 1, 15, 9, 35),
            ),
            Trade(
                symbol="000001", name="平安银行", direction="sell",
                price=11.00, quantity=1000, amount=11000,
                fee=5.50, trade_time=datetime(2024, 1, 17, 14, 30),
            ),
            Trade(
                symbol="600519", name="贵州茅台", direction="buy",
                price=1680.00, quantity=100, amount=168000,
                fee=8.40, trade_time=datetime(2024, 1, 20, 10, 00),
            ),
            Trade(
                symbol="600519", name="贵州茅台", direction="sell",
                price=1700.00, quantity=100, amount=170000,
                fee=8.50, trade_time=datetime(2024, 1, 23, 14, 00),
            ),
        ]
        session.add_all(trades)
        session.commit()
        session.close()

        analyzer = StyleAnalyzer()
        result = analyzer.analyze_style()

        assert result["style_label"] == "短线炒手"
        assert result["avg_holding_days"] < 5
        assert result["concentration"] == 2
        assert result["total_trades"] == 4
        assert result["paired_count"] == 2

    def test_swing_style(self, db_session):
        """测试波段风格判断（5 <= 持仓 < 30天）"""
        from stock_assistant.style.analyzer import StyleAnalyzer

        session = db_session()
        trades = [
            Trade(
                symbol="000001", name="平安银行", direction="buy",
                price=10.50, quantity=1000, amount=10500,
                fee=5.25, trade_time=datetime(2024, 1, 1, 10, 0),
            ),
            Trade(
                symbol="000001", name="平安银行", direction="sell",
                price=11.20, quantity=1000, amount=11200,
                fee=5.60, trade_time=datetime(2024, 1, 16, 14, 0),
            ),
        ]
        session.add_all(trades)
        session.commit()
        session.close()

        analyzer = StyleAnalyzer()
        result = analyzer.analyze_style()

        assert result["style_label"] == "波段操作"
        assert 5 <= result["avg_holding_days"] < 30

    def test_long_term_style(self, db_session):
        """测试中长线风格判断（持仓 >= 30天）"""
        from stock_assistant.style.analyzer import StyleAnalyzer

        session = db_session()
        trades = [
            Trade(
                symbol="600519", name="贵州茅台", direction="buy",
                price=1680.00, quantity=100, amount=168000,
                fee=8.40, trade_time=datetime(2024, 1, 1, 9, 45),
            ),
            Trade(
                symbol="600519", name="贵州茅台", direction="sell",
                price=1800.00, quantity=100, amount=180000,
                fee=9.00, trade_time=datetime(2024, 3, 15, 14, 30),
            ),
        ]
        session.add_all(trades)
        session.commit()
        session.close()

        analyzer = StyleAnalyzer()
        result = analyzer.analyze_style()

        assert result["style_label"] == "中长线投资"
        assert result["avg_holding_days"] >= 30
