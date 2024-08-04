"""
Tool use agent with ollama.
"""

import datetime
import json

import ollama
import streamlit as st

from tool_wrapper import Tool


## define tools
def calculate(expression: str) -> str:
    """Calculate the given expression."""
    allowed_chars = set("0123456789+-*(). /")
    for char in expression:
        if char not in allowed_chars:
            raise ValueError(f"Unsupported character included({char})")
    return str(eval(expression))


def get_datetime() -> str:
    """Get current date and time."""
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

## state initialization

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["content"]:
            st.markdown(msg["content"])
        if 'tool_calls' in msg:
            st.markdown('```json\n' + json.dumps(msg['tool_calls']) + '\n```')

## agent

if user_msg := st.chat_input():
    tools = [Tool(calculate), Tool(get_datetime)]
    st.session_state.messages.append(
        {"role": "user", "content": user_msg})
    st.chat_message("user").write(user_msg)

    for _ in range(10):
        # assistant
        response = ollama.chat(
            model="mistral-nemo",
            messages=st.session_state.messages,
            tools=[t.api_doc for t in tools]
        )
        msg = response["message"]
        st.session_state.messages.append(msg)
        with st.chat_message("assistant"):
            if "tool_calls" in msg:
                st.markdown('```json\n' + json.dumps(msg['tool_calls']) + '\n```')
            else:
                st.markdown(msg["content"])
                break

        # tool execution
        if "tool_calls" in msg:
            tool_dict = {tool.name: tool for tool in tools}
            for tool_call in msg['tool_calls']:
                try:
                    tool = tool_dict[tool_call['function']['name']]
                    ret = tool(**tool_call['function']['arguments'])
                    tool_call_content = ret
                except Exception as e:
                    tool_call_content = 'ERROR: ' + str(e)
                st.session_state.messages.append({
                    'role': 'tool',
                    'content': str(tool_call_content)
                })
                with st.chat_message("tool"):
                    st.markdown(str(tool_call_content))
