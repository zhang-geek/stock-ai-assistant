"""模拟交易 API"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from stock_assistant.paper_trading.engine import PaperTradingEngine

router = APIRouter()


def _get_engine() -> PaperTradingEngine:
    return PaperTradingEngine()


@router.get("/portfolio")
def get_portfolio():
    engine = _get_engine()
    data = engine.get_portfolio()
    # Convert datetime objects to strings for JSON serialization
    for pos in data.get("positions", []):
        if "entry_time" in pos and hasattr(pos["entry_time"], "isoformat"):
            pos["entry_time"] = pos["entry_time"].isoformat()
    return {"data": data}


class TradeRequest(BaseModel):
    symbol: str
    price: float
    quantity: int
    reasoning: str = ""
    strategy: str = "manual"


@router.post("/buy")
def buy_stock(req: TradeRequest):
    engine = _get_engine()
    ok = engine.buy(
        req.symbol, req.price, req.quantity,
        reasoning=req.reasoning, strategy=req.strategy,
    )
    return {"success": ok}


@router.post("/sell")
def sell_stock(req: TradeRequest):
    engine = _get_engine()
    ok = engine.sell(
        req.symbol, req.price, req.quantity,
        reasoning=req.reasoning, strategy=req.strategy,
    )
    return {"success": ok}


@router.get("/history")
def trade_history(n: int = Query(20)):
    engine = _get_engine()
    history = engine.get_history(n)
    for item in history:
        if "timestamp" in item and hasattr(item["timestamp"], "isoformat"):
            item["timestamp"] = item["timestamp"].isoformat()
    return {"data": history}


@router.get("/decision/{symbol}")
async def ai_decision(symbol: str):
    from stock_assistant.paper_trading.agents import multi_agent_decision
    result = await multi_agent_decision(symbol)
    return {"data": result}
