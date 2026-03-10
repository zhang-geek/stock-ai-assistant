"""首页：主要指数 + 涨跌幅排行 + 板块排行"""

import streamlit as st
import pandas as pd
import yaml
from pathlib import Path

from stock_assistant.data.akshare_source import get_data_source


@st.cache_data(ttl=300)
def _fetch_index_quote() -> pd.DataFrame:
    return get_data_source().get_index_quote()


@st.cache_data(ttl=300)
def _fetch_top_gainers(n: int = 5) -> pd.DataFrame:
    return get_data_source().get_top_gainers(n)


@st.cache_data(ttl=300)
def _fetch_top_losers(n: int = 5) -> pd.DataFrame:
    return get_data_source().get_top_losers(n)


@st.cache_data(ttl=300)
def _fetch_sector_performance() -> pd.DataFrame:
    return get_data_source().get_sector_performance()


@st.cache_data(ttl=300)
def _fetch_watchlist_quote(symbols: tuple[str, ...]) -> pd.DataFrame:
    return get_data_source().get_realtime_quote(list(symbols))


def _load_watchlist() -> list[dict]:
    config_path = Path(__file__).resolve().parents[4] / "config" / "watchlist.yaml"
    if not config_path.exists():
        return []
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("watchlist", [])


def render():
    st.title("A股AI助手 - 首页")

    # --- 主要指数 ---
    st.subheader("主要指数")
    try:
        idx_df = _fetch_index_quote()
        cols = st.columns(len(idx_df))
        for col, (_, row) in zip(cols, idx_df.iterrows()):
            with col:
                change_pct = row["change_pct"]
                st.metric(
                    label=row["name"],
                    value=f"{row['price']:.2f}",
                    delta=f"{change_pct:+.2f}%",
                )
    except Exception as e:
        st.error(f"获取指数数据失败: {e}")

    st.divider()

    # --- 自选股 ---
    watchlist = _load_watchlist()
    if watchlist:
        st.subheader("自选股")
        symbols = tuple(item["symbol"] for item in watchlist)
        try:
            wl_df = _fetch_watchlist_quote(symbols)
            st.dataframe(
                wl_df[["symbol", "name", "price", "change_pct", "volume", "amount"]],
                use_container_width=True,
                hide_index=True,
            )
        except Exception as e:
            st.error(f"获取自选股数据失败: {e}")
        st.divider()

    # --- 涨跌幅排行 ---
    col_gain, col_lose = st.columns(2)
    with col_gain:
        st.subheader("涨幅 TOP 5")
        try:
            gainers = _fetch_top_gainers(5)
            st.dataframe(
                gainers[["symbol", "name", "price", "change_pct"]],
                use_container_width=True,
                hide_index=True,
            )
        except Exception as e:
            st.error(f"获取涨幅榜失败: {e}")

    with col_lose:
        st.subheader("跌幅 TOP 5")
        try:
            losers = _fetch_top_losers(5)
            st.dataframe(
                losers[["symbol", "name", "price", "change_pct"]],
                use_container_width=True,
                hide_index=True,
            )
        except Exception as e:
            st.error(f"获取跌幅榜失败: {e}")

    st.divider()

    # --- 板块排行 ---
    st.subheader("板块涨跌幅 TOP 10")
    try:
        sector_df = _fetch_sector_performance()
        sector_df = sector_df.sort_values("change_pct", ascending=False).head(10)
        st.dataframe(
            sector_df[["sector", "change_pct", "up_count", "down_count"]],
            use_container_width=True,
            hide_index=True,
        )
    except Exception as e:
        st.error(f"获取板块数据失败: {e}")
