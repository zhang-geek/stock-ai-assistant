"""费用统计 API"""

from fastapi import APIRouter, Query

from stock_assistant.llm.cost_tracker import get_cost_summary

router = APIRouter()


@router.get("/summary")
def cost_summary(days: int = Query(30, description="统计天数")):
    summary = get_cost_summary(days)
    return {"data": summary}
