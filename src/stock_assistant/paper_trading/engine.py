"""模拟交易引擎"""

from __future__ import annotations

from datetime import datetime

from stock_assistant.core.config import get_settings
from stock_assistant.core.database import get_session
from stock_assistant.core.models import PaperPosition, PaperTransaction
from stock_assistant.data.akshare_source import get_data_source

# 默认策略名
DEFAULT_STRATEGY = "manual"


class PaperTradingEngine:
    """模拟交易引擎"""

    def __init__(self):
        settings = get_settings()
        self.initial_capital = settings.paper_trading.initial_capital
        self.max_position_pct = settings.paper_trading.max_position_pct

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _get_open_positions(self, session) -> list[PaperPosition]:
        """查询所有未平仓持仓"""
        return session.query(PaperPosition).filter_by(status="open").all()

    def _used_capital(self, session) -> float:
        """已占用资金 = 所有 open 持仓的买入金额之和"""
        positions = self._get_open_positions(session)
        return sum(p.entry_price * p.quantity for p in positions)

    def _available_cash(self, session) -> float:
        """可用现金"""
        return self.initial_capital - self._used_capital(session)

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def get_portfolio(self) -> dict:
        """获取当前模拟投资组合"""
        session = get_session()
        try:
            positions = self._get_open_positions(session)

            # 更新当前价格
            if positions:
                symbols = [p.symbol for p in positions]
                ds = get_data_source()
                df = ds.get_realtime_quote(symbols)
                price_map = {}
                if not df.empty:
                    price_map = dict(zip(df["symbol"].astype(str), df["price"]))

                for p in positions:
                    if p.symbol in price_map:
                        p.current_price = price_map[p.symbol]
                session.commit()

            # 计算组合指标
            cash = self._available_cash(session)
            market_value = sum(
                (p.current_price or p.entry_price) * p.quantity for p in positions
            )
            total_value = cash + market_value
            total_pnl = total_value - self.initial_capital
            pnl_pct = total_pnl / self.initial_capital * 100 if self.initial_capital else 0

            pos_list = []
            for p in positions:
                cur = p.current_price or p.entry_price
                pnl = (cur - p.entry_price) * p.quantity
                pnl_pct_item = (cur - p.entry_price) / p.entry_price * 100
                pos_list.append({
                    "id": p.id,
                    "symbol": p.symbol,
                    "name": p.name or p.symbol,
                    "quantity": p.quantity,
                    "entry_price": p.entry_price,
                    "current_price": cur,
                    "market_value": cur * p.quantity,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct_item,
                    "entry_time": p.entry_time,
                })

            return {
                "capital": self.initial_capital,
                "cash": cash,
                "market_value": market_value,
                "total_value": total_value,
                "total_pnl": total_pnl,
                "pnl_pct": pnl_pct,
                "positions": pos_list,
            }
        finally:
            session.close()

    def buy(
        self,
        symbol: str,
        price: float,
        quantity: int,
        reasoning: str = "",
        strategy: str = DEFAULT_STRATEGY,
    ) -> bool:
        """模拟买入

        返回是否成功
        """
        session = get_session()
        try:
            cost = price * quantity

            # 1. 检查可用资金
            cash = self._available_cash(session)
            if cost > cash:
                return False

            # 2. 检查单股仓位限制
            if cost > self.initial_capital * self.max_position_pct:
                return False

            # 3. 创建持仓
            pos = PaperPosition(
                strategy_name=strategy,
                symbol=symbol,
                direction="long",
                entry_price=price,
                quantity=quantity,
                current_price=price,
                entry_time=datetime.now(),
                status="open",
            )
            session.add(pos)

            # 4. 记录交易流水
            tx = PaperTransaction(
                strategy_name=strategy,
                symbol=symbol,
                action="buy",
                price=price,
                quantity=quantity,
                reasoning=reasoning,
                timestamp=datetime.now(),
            )
            session.add(tx)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def sell(
        self,
        symbol: str,
        price: float,
        quantity: int = 0,
        reasoning: str = "",
        strategy: str = DEFAULT_STRATEGY,
    ) -> bool:
        """模拟卖出

        quantity=0 表示卖出该股全部持仓。返回是否成功。
        """
        session = get_session()
        try:
            # 查找该股的 open 持仓
            positions = (
                session.query(PaperPosition)
                .filter_by(symbol=symbol, status="open")
                .all()
            )
            if not positions:
                return False

            # 计算总持仓量
            total_qty = sum(p.quantity for p in positions)
            sell_qty = quantity if quantity > 0 else total_qty
            if sell_qty > total_qty:
                return False

            # 按先进先出逐笔平仓
            remaining = sell_qty
            for p in positions:
                if remaining <= 0:
                    break
                if p.quantity <= remaining:
                    # 整笔平仓
                    p.status = "closed"
                    p.exit_price = price
                    p.exit_time = datetime.now()
                    p.pnl = (price - p.entry_price) * p.quantity
                    remaining -= p.quantity
                else:
                    # 部分平仓：拆分持仓
                    # 关闭 remaining 部分
                    p.quantity -= remaining
                    closed = PaperPosition(
                        strategy_name=p.strategy_name,
                        symbol=p.symbol,
                        name=p.name,
                        direction=p.direction,
                        entry_price=p.entry_price,
                        quantity=remaining,
                        current_price=price,
                        entry_time=p.entry_time,
                        exit_time=datetime.now(),
                        exit_price=price,
                        pnl=(price - p.entry_price) * remaining,
                        status="closed",
                    )
                    session.add(closed)
                    remaining = 0

            # 记录交易流水
            tx = PaperTransaction(
                strategy_name=strategy,
                symbol=symbol,
                action="sell",
                price=price,
                quantity=sell_qty,
                reasoning=reasoning,
                timestamp=datetime.now(),
            )
            session.add(tx)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def get_history(self, n: int = 20) -> list[dict]:
        """获取最近的交易历史"""
        session = get_session()
        try:
            txs = (
                session.query(PaperTransaction)
                .order_by(PaperTransaction.timestamp.desc())
                .limit(n)
                .all()
            )
            return [
                {
                    "id": t.id,
                    "strategy": t.strategy_name,
                    "symbol": t.symbol,
                    "action": t.action,
                    "price": t.price,
                    "quantity": t.quantity,
                    "reasoning": t.reasoning or "",
                    "timestamp": t.timestamp,
                }
                for t in txs
            ]
        finally:
            session.close()
