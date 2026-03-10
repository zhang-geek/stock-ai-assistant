"""AI多轮对话"""

import asyncio

import streamlit as st

from stock_assistant.llm.router import get_router


def render():
    st.title("AI问答")

    # 初始化对话历史
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 渲染历史消息
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 用户输入
    user_input = st.chat_input("输入你的问题，例如：贵州茅台近期走势如何？")

    if user_input:
        # 显示用户消息
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 调用LLM获取回答
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    router = get_router()
                    answer = asyncio.run(router.ask(user_input))
                    st.markdown(answer)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception as e:
                    error_msg = f"调用LLM失败: {e}"
                    st.error(error_msg)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": error_msg}
                    )

    # 侧边栏清空按钮
    if st.sidebar.button("清空对话"):
        st.session_state.chat_history = []
        st.rerun()
