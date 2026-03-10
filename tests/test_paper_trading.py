"""模拟交易模块测试"""

from __future__ import annotations


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from stock_assistant.core.models import Base, PaperPosition, PaperTransaction


@pytest.fixture()
def db_session(monkeypatch):
    """使用内存SQLite数据库"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    import stock_assistant.core.database as db_mod
    monkeypatch.setattr(db_mod, "get_session", factory)

    import stock_assistant.paper_trading.engine as eng_mod
    monkeypatch.setattr(eng_mod, "get_session", factory)

    return factory


@pytest.fixture()
def engine(db_session, monkeypatch):
    """创建测试用交易引擎（初始资金100万，单股上限10%）"""
    from stock_assistant.paper_trading.engine import PaperTradingEngine

    eng = PaperTradingEngine.__new__(PaperTradingEngine)
    eng.initial_capital = 1_000_000
    eng.max_position_pct = 0.10
    return eng


class TestPaperTradingEngine:
    """交易引擎测试"""

    def test_buy_success(self, engine, db_session):
        """正常买入"""
        ok = engine.buy("000001", 10.0, 100, reasoning="测试买入")
        assert ok is True

        # 验证数据库
        session = db_session()
        positions = session.query(PaperPosition).filter_by(status="open").all()
        assert len(positions) == 1
        assert positions[0].symbol == "000001"
        assert positions[0].entry_price == 10.0
        assert positions[0].quantity == 100

        txs = session.query(PaperTransaction).all()
        assert len(txs) == 1
        assert txs[0].action == "buy"
        session.close()

    def test_buy_insufficient_funds(self, engine, db_session):
        """资金不足时买入失败"""
        # 初始资金100万，买入超过100万应失败
        ok = engine.buy("000001", 100.0, 20000, reasoning="大额买入")
        assert ok is False

        session = db_session()
        assert session.query(PaperPosition).count() == 0
        session.close()

    def test_buy_exceeds_position_limit(self, engine, db_session):
        """超过单股仓位限制时买入失败"""
        # 单股上限10%=10万，买入超过10万应失败
        ok = engine.buy("000001", 20.0, 6000, reasoning="超限买入")
        # 20 * 6000 = 120000 > 100000
        assert ok is False

    def test_buy_within_position_limit(self, engine, db_session):
        """在仓位限制内买入成功"""
        # 10万以内应该成功
        ok = engine.buy("000001", 10.0, 1000, reasoning="限内买入")
        # 10 * 1000 = 10000 < 100000
        assert ok is True

    def test_sell_success(self, engine, db_session):
        """正常卖出"""
        engine.buy("000001", 10.0, 100)
        ok = engine.sell("000001", 12.0, 100, reasoning="测试卖出")
        assert ok is True

        session = db_session()
        pos = session.query(PaperPosition).filter_by(status="closed").first()
        assert pos is not None
        assert pos.exit_price == 12.0
        assert pos.pnl == pytest.approx(200.0)  # (12-10)*100

        txs = session.query(PaperTransaction).filter_by(action="sell").all()
        assert len(txs) == 1
        session.close()

    def test_sell_all(self, engine, db_session):
        """quantity=0 卖出全部"""
        engine.buy("000001", 10.0, 200)
        ok = engine.sell("000001", 11.0, 0)  # 0=全部
        assert ok is True

        session = db_session()
        open_pos = session.query(PaperPosition).filter_by(status="open").count()
        assert open_pos == 0
        session.close()

    def test_sell_no_position(self, engine, db_session):
        """没有持仓时卖出失败"""
        ok = engine.sell("000001", 10.0, 100)
        assert ok is False

    def test_sell_exceeds_quantity(self, engine, db_session):
        """卖出数量超过持仓时失败"""
        engine.buy("000001", 10.0, 100)
        ok = engine.sell("000001", 10.0, 200)
        assert ok is False

    def test_portfolio_calculation(self, engine, db_session, monkeypatch):
        """测试组合计算"""
        # 买入两只股票
        engine.buy("000001", 10.0, 100)
        engine.buy("600519", 1680.0, 5)

        # mock实时行情（不调用真实API）
        import pandas as pd
        mock_df = pd.DataFrame([
            {"symbol": "000001", "name": "平安银行", "price": 11.0},
            {"symbol": "600519", "name": "贵州茅台", "price": 1700.0},
        ])

        class FakeDS:
            def get_realtime_quote(self, symbols):
                return mock_df

        monkeypatch.setattr(
            "stock_assistant.paper_trading.engine.get_data_source",
            lambda: FakeDS(),
        )

        portfolio = engine.get_portfolio()

        assert portfolio["capital"] == 1_000_000
        # 已占用: 10*100 + 1680*5 = 1000 + 8400 = 9400
        assert portfolio["cash"] == pytest.approx(1_000_000 - 9400)
        # 市值: 11*100 + 1700*5 = 1100 + 8500 = 9600
        assert portfolio["market_value"] == pytest.approx(9600.0)
        assert portfolio["total_value"] == pytest.approx(1_000_000 - 9400 + 9600)
        assert portfolio["total_pnl"] == pytest.approx(200.0)  # 9600 - 9400
        assert len(portfolio["positions"]) == 2

    def test_history(self, engine, db_session):
        """测试交易历史"""
        engine.buy("000001", 10.0, 100, reasoning="买入测试")
        engine.sell("000001", 11.0, 100, reasoning="卖出测试")

        records = engine.get_history(10)
        assert len(records) == 2
        # 最新的排前面
        assert records[0]["action"] == "sell"
        assert records[1]["action"] == "buy"

    def test_multiple_buys_cash_tracking(self, engine, db_session):
        """多次买入后可用资金正确减少"""
        engine.buy("000001", 10.0, 1000)  # 占用 10000
        engine.buy("000002", 8.0, 1000)   # 占用 8000

        session = db_session()
        cash = engine._available_cash(session)
        assert cash == pytest.approx(1_000_000 - 18000)
        session.close()


class TestMultiAgentDecision:
    """多Agent决策投票逻辑测试"""

    @pytest.mark.asyncio
    async def test_voting_logic(self, db_session, monkeypatch):
        """测试加权投票：多数买入 → 最终买入"""
        from stock_assistant.paper_trading.agents import (
            AgentSignal,
            multi_agent_decision,
        )
        from stock_assistant.paper_trading.engine import PaperTradingEngine

        # mock get_data_source
        import pandas as pd
        mock_df = pd.DataFrame([
            {"symbol": "000001", "name": "平安银行", "price": 10.0, "change_pct": 2.5},
        ])

        class FakeDS:
            def get_realtime_quote(self, symbols):
                return mock_df

        monkeypatch.setattr(
            "stock_assistant.paper_trading.agents.get_data_source",
            lambda: FakeDS(),
        )
        monkeypatch.setattr(
            "stock_assistant.paper_trading.engine.get_data_source",
            lambda: FakeDS(),
        )

        # mock PaperTradingEngine（避免真实配置依赖）
        eng = PaperTradingEngine.__new__(PaperTradingEngine)
        eng.initial_capital = 1_000_000
        eng.max_position_pct = 0.10
        monkeypatch.setattr(
            "stock_assistant.paper_trading.engine.PaperTradingEngine",
            lambda: eng,
        )

        # mock 所有Agent的analyze方法
        buy_signal = AgentSignal("technical", "buy", 0.8, "技术面看多")
        hold_signal = AgentSignal("fundamental", "buy", 0.7, "基本面稳健")
        sentiment_signal = AgentSignal("sentiment", "hold", 0.5, "情绪中性")
        risk_signal = AgentSignal("risk", "buy", 0.6, "风险可控")

        async def mock_analyze(self, symbol, context):
            mapping = {
                "technical": buy_signal,
                "fundamental": hold_signal,
                "sentiment": sentiment_signal,
                "risk": risk_signal,
            }
            return mapping[self.name]

        from stock_assistant.paper_trading import agents as agents_mod
        monkeypatch.setattr(agents_mod.TechnicalAgent, "analyze", mock_analyze)
        monkeypatch.setattr(agents_mod.FundamentalAgent, "analyze", mock_analyze)
        monkeypatch.setattr(agents_mod.SentimentAgent, "analyze", mock_analyze)
        monkeypatch.setattr(agents_mod.RiskAgent, "analyze", mock_analyze)

        result = await multi_agent_decision("000001")

        assert result["action"] == "buy"
        assert result["weighted_score"] > 0.2
        assert len(result["agents"]) == 4

    @pytest.mark.asyncio
    async def test_voting_hold(self, db_session, monkeypatch):
        """测试加权投票：意见分歧 → hold"""
        from stock_assistant.paper_trading.agents import (
            AgentSignal,
            multi_agent_decision,
        )
        from stock_assistant.paper_trading.engine import PaperTradingEngine

        import pandas as pd
        mock_df = pd.DataFrame([
            {"symbol": "000001", "name": "平安银行", "price": 10.0, "change_pct": 0.1},
        ])

        class FakeDS:
            def get_realtime_quote(self, symbols):
                return mock_df

        monkeypatch.setattr(
            "stock_assistant.paper_trading.agents.get_data_source",
            lambda: FakeDS(),
        )
        monkeypatch.setattr(
            "stock_assistant.paper_trading.engine.get_data_source",
            lambda: FakeDS(),
        )

        eng = PaperTradingEngine.__new__(PaperTradingEngine)
        eng.initial_capital = 1_000_000
        eng.max_position_pct = 0.10
        monkeypatch.setattr(
            "stock_assistant.paper_trading.engine.PaperTradingEngine",
            lambda: eng,
        )

        # 意见分歧：买卖各半
        signals = {
            "technical": AgentSignal("technical", "buy", 0.6, "看多"),
            "fundamental": AgentSignal("fundamental", "sell", 0.6, "看空"),
            "sentiment": AgentSignal("sentiment", "hold", 0.5, "中性"),
            "risk": AgentSignal("risk", "hold", 0.5, "观望"),
        }

        async def mock_analyze(self, symbol, context):
            return signals[self.name]

        from stock_assistant.paper_trading import agents as agents_mod
        monkeypatch.setattr(agents_mod.TechnicalAgent, "analyze", mock_analyze)
        monkeypatch.setattr(agents_mod.FundamentalAgent, "analyze", mock_analyze)
        monkeypatch.setattr(agents_mod.SentimentAgent, "analyze", mock_analyze)
        monkeypatch.setattr(agents_mod.RiskAgent, "analyze", mock_analyze)

        result = await multi_agent_decision("000001")

        assert result["action"] == "hold"
