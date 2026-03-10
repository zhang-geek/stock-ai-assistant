"""风格探索 API"""

from fastapi import APIRouter
from pydantic import BaseModel

from stock_assistant.backtest.analyzer import TradeAnalyzer
from stock_assistant.style.analyzer import StyleAnalyzer

router = APIRouter()


@router.get("/analyze")
def analyze_style():
    analyzer = StyleAnalyzer()
    style_data = analyzer.analyze_style()
    return {"data": style_data}


class CoachRequest(BaseModel):
    question: str = ""


@router.post("/coach")
async def ai_coach(req: CoachRequest):
    style_analyzer = StyleAnalyzer()
    trade_analyzer = TradeAnalyzer()
    style_data = style_analyzer.analyze_style()
    stats = trade_analyzer.get_statistics()
    result = await style_analyzer.ai_coach(style_data, stats)
    return {"data": result}
