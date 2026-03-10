"""API费用追踪"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func

from stock_assistant.core.database import get_session
from stock_assistant.core.models import LLMUsage


def get_cost_summary(days: int = 30) -> dict:
    """获取指定天数内的费用汇总"""
    session = get_session()
    since = datetime.now() - timedelta(days=days)

    rows = (
        session.query(
            LLMUsage.provider,
            LLMUsage.task_type,
            func.count(LLMUsage.id).label("calls"),
            func.sum(LLMUsage.input_tokens).label("input_tokens"),
            func.sum(LLMUsage.output_tokens).label("output_tokens"),
            func.sum(LLMUsage.cost_usd).label("total_cost"),
        )
        .filter(LLMUsage.timestamp >= since)
        .group_by(LLMUsage.provider, LLMUsage.task_type)
        .all()
    )

    session.close()

    summary = {
        "period_days": days,
        "by_provider": {},
        "by_task": {},
        "total_cost_usd": 0,
        "total_calls": 0,
    }

    for row in rows:
        provider, task, calls, in_tok, out_tok, cost = row
        cost = cost or 0

        summary["total_cost_usd"] += cost
        summary["total_calls"] += calls

        if provider not in summary["by_provider"]:
            summary["by_provider"][provider] = {"calls": 0, "cost": 0}
        summary["by_provider"][provider]["calls"] += calls
        summary["by_provider"][provider]["cost"] += cost

        if task not in summary["by_task"]:
            summary["by_task"][task] = {"calls": 0, "cost": 0}
        summary["by_task"][task]["calls"] += calls
        summary["by_task"][task]["cost"] += cost

    return summary
