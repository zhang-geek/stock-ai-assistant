"""市场监控 API"""

from fastapi import APIRouter, Query

from stock_assistant.market.analyzer import MarketAnalyzer

router = APIRouter()


@router.get("/morning-brief")
async def morning_brief():
    analyzer = MarketAnalyzer()
    result = await analyzer.morning_brief()
    return {"data": result}


@router.get("/evening-review")
async def evening_review():
    analyzer = MarketAnalyzer()
    result = await analyzer.evening_review()
    return {"data": result}


@router.get("/signals")
async def scan_signals(threshold: float = Query(5.0, description="异动阈值(涨跌幅%)")):
    analyzer = MarketAnalyzer()
    signals = await analyzer.scan_signals(threshold=threshold)
    return {"data": signals}
