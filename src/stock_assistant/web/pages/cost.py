"""API费用统计"""

import streamlit as st
import pandas as pd

from stock_assistant.llm.cost_tracker import get_cost_summary
from stock_assistant.core.database import get_session, init_db
from stock_assistant.core.models import LLMUsage


def render():
    st.title("API费用统计")

    # 确保数据库表存在
    try:
        init_db()
    except Exception:
        pass

    # 统计天数选择
    days = st.slider("统计天数", min_value=1, max_value=90, value=30)

    try:
        summary = get_cost_summary(days=days)
    except Exception as e:
        st.error(f"获取费用数据失败: {e}")
        return

    # --- 总览 ---
    c1, c2 = st.columns(2)
    with c1:
        st.metric("总调用次数", f"{summary['total_calls']}")
    with c2:
        st.metric("总费用 (USD)", f"${summary['total_cost_usd']:.4f}")

    st.divider()

    # --- 按 Provider 分布 ---
    st.subheader("按 Provider 统计")
    by_provider = summary.get("by_provider", {})
    if by_provider:
        provider_rows = [
            {"Provider": k, "调用次数": v["calls"], "费用(USD)": round(v["cost"], 4)}
            for k, v in by_provider.items()
        ]
        provider_df = pd.DataFrame(provider_rows)
        st.dataframe(provider_df, use_container_width=True, hide_index=True)

        # 柱状图
        chart_df = provider_df.set_index("Provider")
        st.bar_chart(chart_df["费用(USD)"], use_container_width=True)
    else:
        st.info(f"近{days}天内无API调用记录")

    st.divider()

    # --- 按任务类型分布 ---
    st.subheader("按任务类型统计")
    by_task = summary.get("by_task", {})
    if by_task:
        task_rows = [
            {"任务类型": k, "调用次数": v["calls"], "费用(USD)": round(v["cost"], 4)}
            for k, v in by_task.items()
        ]
        task_df = pd.DataFrame(task_rows)
        st.dataframe(task_df, use_container_width=True, hide_index=True)
    else:
        st.info("暂无任务类型数据")

    st.divider()

    # --- 最近调用记录 ---
    st.subheader("最近调用记录")
    try:
        session = get_session()
        records = (
            session.query(LLMUsage)
            .order_by(LLMUsage.timestamp.desc())
            .limit(20)
            .all()
        )
        session.close()

        if records:
            rows = [
                {
                    "时间": r.timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.timestamp else "",
                    "Provider": r.provider,
                    "模型": r.model,
                    "任务": r.task_type or "",
                    "输入Tokens": r.input_tokens,
                    "输出Tokens": r.output_tokens,
                    "费用(USD)": round(r.cost_usd or 0, 6),
                }
                for r in records
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("暂无调用记录")
    except Exception as e:
        st.warning(f"获取调用记录失败: {e}")
