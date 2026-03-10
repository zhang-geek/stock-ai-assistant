"""自选股 API"""

from fastapi import APIRouter
from pydantic import BaseModel

from stock_assistant.core.database import get_session
from stock_assistant.core.models import Watchlist

router = APIRouter()


@router.get("")
def list_watchlist():
    session = get_session()
    items = session.query(Watchlist).order_by(Watchlist.added_at.desc()).all()
    session.close()
    data = []
    for item in items:
        data.append({
            "id": item.id,
            "symbol": item.symbol,
            "name": item.name,
            "sector": item.sector,
            "notes": item.notes,
            "added_at": item.added_at.isoformat() if item.added_at else None,
        })
    return {"data": data}


class AddWatchlistRequest(BaseModel):
    symbol: str
    name: str = ""
    sector: str = ""
    notes: str = ""


@router.post("")
def add_to_watchlist(req: AddWatchlistRequest):
    session = get_session()
    existing = session.query(Watchlist).filter(Watchlist.symbol == req.symbol).first()
    if existing:
        session.close()
        return {"success": False, "message": "已存在"}

    item = Watchlist(
        symbol=req.symbol,
        name=req.name,
        sector=req.sector,
        notes=req.notes,
    )
    session.add(item)
    session.commit()
    session.close()
    return {"success": True}


@router.delete("/{symbol}")
def remove_from_watchlist(symbol: str):
    session = get_session()
    item = session.query(Watchlist).filter(Watchlist.symbol == symbol).first()
    if item:
        session.delete(item)
        session.commit()
    session.close()
    return {"success": True}
