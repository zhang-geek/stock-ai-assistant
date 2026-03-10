"""Streamlit Web 应用入口"""

import streamlit as st

st.set_page_config(
    page_title="A股AI助手",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 侧边栏导航
st.sidebar.title("A股AI助手")
page = st.sidebar.radio("导航", ["🏠 首页", "📊 行情", "💬 AI问答", "💰 API费用"])

if page == "🏠 首页":
    from stock_assistant.web.pages import home
    home.render()
elif page == "📊 行情":
    from stock_assistant.web.pages import quote
    quote.render()
elif page == "💬 AI问答":
    from stock_assistant.web.pages import chat
    chat.render()
elif page == "💰 API费用":
    from stock_assistant.web.pages import cost
    cost.render()
