"""行情 API"""

from fastapi import APIRouter, Query

from stock_assistant.api.deps import get_ds

router = APIRouter()


@router.get("/realtime")
def realtime_quote(symbols: str = Query(..., description="逗号分隔的股票代码")):
    ds = get_ds()
    symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
    df = ds.get_realtime_quote(symbol_list)
    return {"data": df.to_dict(orient="records")}


@router.get("/daily/{symbol}")
def daily_bars(
    symbol: str,
    start: str = Query("", description="开始日期 YYYYMMDD"),
    end: str = Query("", description="结束日期 YYYYMMDD"),
    adjust: str = Query("qfq", description="复权: qfq/hfq/空"),
):
    ds = get_ds()
    df = ds.get_daily_bars(symbol, start=start, end=end, adjust=adjust)
    # Convert date column to string for JSON serialization
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return {"data": df.to_dict(orient="records")}


@router.get("/index")
def index_quote():
    ds = get_ds()
    df = ds.get_index_quote()
    return {"data": df.to_dict(orient="records")}


@router.get("/sectors")
def sector_performance(n: int = Query(20, description="返回条数")):
    ds = get_ds()
    df = ds.get_sector_performance()
    return {"data": df.head(n).to_dict(orient="records")}


@router.get("/top/gainers")
def top_gainers(n: int = Query(20)):
    ds = get_ds()
    df = ds.get_top_gainers(n)
    return {"data": df.to_dict(orient="records")}


@router.get("/top/losers")
def top_losers(n: int = Query(20)):
    ds = get_ds()
    df = ds.get_top_losers(n)
    return {"data": df.to_dict(orient="records")}


@router.get("/news")
def stock_news(symbol: str = Query("", description="股票代码，空则获取全局新闻")):
    ds = get_ds()
    df = ds.get_news(symbol)
    return {"data": df.head(30).to_dict(orient="records")}


@router.get("/info/{symbol}")
def stock_info(symbol: str):
    ds = get_ds()
    info = ds.get_stock_info(symbol)
    return {"data": info}
