"""个股行情查询"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from stock_assistant.data.akshare_source import get_data_source


@st.cache_data(ttl=300)
def _fetch_realtime(symbol: str) -> pd.DataFrame:
    return get_data_source().get_realtime_quote([symbol])


@st.cache_data(ttl=300)
def _fetch_daily_bars(symbol: str, start: str, end: str) -> pd.DataFrame:
    return get_data_source().get_daily_bars(symbol, start=start, end=end)


def render():
    st.title("个股行情查询")

    col_input, col_btn = st.columns([3, 1])
    with col_input:
        symbol = st.text_input("股票代码", placeholder="例如 600519")
    with col_btn:
        st.write("")  # 占位对齐
        st.write("")
        query = st.button("查询", use_container_width=True)

    if not symbol:
        st.info("请输入股票代码后点击查询")
        return

    if not query and "last_quote_symbol" not in st.session_state:
        return

    if query:
        st.session_state["last_quote_symbol"] = symbol

    symbol = st.session_state.get("last_quote_symbol", symbol).strip()

    # --- 实时行情 ---
    st.subheader("实时行情")
    try:
        df = _fetch_realtime(symbol)
        if df.empty:
            st.warning(f"未找到股票 {symbol}")
            return
        row = df.iloc[0]
        st.markdown(f"### {row['name']}（{row['symbol']}）")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("最新价", f"{row['price']:.2f}", delta=f"{row['change_pct']:+.2f}%")
        with c2:
            st.metric("今开", f"{row['open']:.2f}")
        with c3:
            st.metric("最高", f"{row['high']:.2f}")
        with c4:
            st.metric("最低", f"{row['low']:.2f}")

        c5, c6, c7 = st.columns(3)
        with c5:
            st.metric("昨收", f"{row['prev_close']:.2f}")
        with c6:
            vol = row["volume"]
            vol_str = f"{vol / 10000:.1f}万手" if vol >= 10000 else f"{vol:.0f}手"
            st.metric("成交量", vol_str)
        with c7:
            amt = row["amount"]
            amt_str = f"{amt / 1e8:.2f}亿" if amt >= 1e8 else f"{amt / 1e4:.1f}万"
            st.metric("成交额", amt_str)
    except Exception as e:
        st.error(f"获取实时行情失败: {e}")
        return

    st.divider()

    # --- K线图 ---
    st.subheader("近60个交易日K线")
    try:
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=120)).strftime("%Y%m%d")
        bars = _fetch_daily_bars(symbol, start_date, end_date)
        if bars.empty:
            st.warning("暂无K线数据")
            return
        bars = bars.tail(60)

        # 收盘价走势
        chart_data = bars.set_index("date")[["close", "open", "high", "low"]]
        st.line_chart(chart_data["close"], use_container_width=True)

        # 成交量柱状图
        st.bar_chart(bars.set_index("date")["volume"], use_container_width=True)

        # 原始数据折叠展示
        with st.expander("查看K线原始数据"):
            display_cols = ["date", "open", "close", "high", "low", "volume", "change_pct", "turnover"]
            available = [c for c in display_cols if c in bars.columns]
            st.dataframe(bars[available], use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"获取K线数据失败: {e}")
