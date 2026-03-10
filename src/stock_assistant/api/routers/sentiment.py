"""舆情分析 API"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from stock_assistant.sentiment.analyzer import SentimentAnalyzer
from stock_assistant.sentiment.scraper import fetch_posts

router = APIRouter()


class AnalyzeRequest(BaseModel):
    symbol: str
    limit: int = 20


@router.post("/analyze")
async def analyze_sentiment(req: AnalyzeRequest):
    posts = await fetch_posts(req.symbol, limit=req.limit)
    analyzer = SentimentAnalyzer()
    analyzed = await analyzer.analyze_posts(posts, req.symbol)
    count = analyzer.save_to_db(analyzed, req.symbol)
    return {"data": analyzed, "saved_count": count}


@router.get("/daily-summary")
async def daily_summary(symbol: str = Query(None, description="股票代码，空则全市场")):
    analyzer = SentimentAnalyzer()
    result = await analyzer.daily_summary(symbol)
    return {"data": result}
