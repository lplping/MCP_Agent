#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ping
# datetime:2025/4/9 16:51
import streamlit as st
import asyncio
from agent import AgentAI 


st.set_page_config(page_title="Agent对话", layout="wide")
st.title("🤖 多步智能查询助手")


if "messages" not in st.session_state:
    st.session_state.messages = []


if "agent" not in st.session_state:
    st.session_state.agent = AgentAI()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入
prompt = st.chat_input("请输入你的问题...")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("正在思考并调用工具中..."):
            # 调用保留在 session_state 中的 agent 实例
            result = asyncio.run(st.session_state.agent.process_query(prompt))

            # 使用原始的分块格式展示
            st.markdown("### 🧠 思考过程")
            st.info(result["think"])

            for i, step in enumerate(result["steps"]):
                with st.expander(f"📌 第 {i + 1} 步：{step['original_query']}"):
                    if step["tool_call"]:
                        tool = step["tool_call"]
                        st.markdown(f"**调用工具**：{tool['tool_name']}")
                        st.json(tool["tool_args"])
                        st.success(f"🔧 工具返回：{tool['tool_result']}")


            st.markdown("### ✅ 最终总结回答")
            st.success(result["final_summary"])

            # 这一轮的 assistant
            st.session_state.messages.append({
                "role": "assistant",
                "content": "### 🧠 思考过程\n\n（见上方分块展示）\n\n### ✅ 最终总结回答\n\n" + result["final_summary"]
            })
