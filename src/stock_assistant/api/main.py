"""FastAPI 应用入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from stock_assistant.core.database import init_db

from .routers import (
    backtest,
    chat,
    cost,
    financial,
    market,
    paper,
    quote,
    sentiment,
    style,
    watchlist,
)

app = FastAPI(title="A股AI助手 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quote.router, prefix="/api/quote", tags=["行情"])
app.include_router(market.router, prefix="/api/market", tags=["市场"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["舆情"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["回测"])
app.include_router(style.router, prefix="/api/style", tags=["风格"])
app.include_router(paper.router, prefix="/api/paper", tags=["模拟交易"])
app.include_router(financial.router, prefix="/api/financial", tags=["财报"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI问答"])
app.include_router(cost.router, prefix="/api/cost", tags=["费用"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["自选股"])


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
