import asyncio
import streamlit as st
from utils.config import get_credentials
from utils.read_local_data import read_local_data
from utils.rag_system import get_emebedding_model, get_llm, build_connections, build_query_engine, build_agent
import traceback
from llama_index.core.workflow import Context
# from utils.observability import init_instrumentor

MAX_REQUESTS = 5

@st.cache_resource
def get_cached_embedding_model():
    return get_emebedding_model(st.session_state.credentials.get("HF_TOKEN"))

@st.cache_resource
def get_cached_connections():
    return build_connections(st.session_state.credentials)

@st.cache_resource
def get_cached_prompt():
    return read_local_data("system_prompt_v3.md")

@st.cache_resource
def get_cached_llm(prompt):
    return get_llm(st.session_state.credentials, prompt)

@st.cache_resource
def load_rag_system():
    prompt = get_cached_prompt()
    llm = get_cached_llm(prompt)
    embedding_model = get_cached_embedding_model()
    pinecone_index, docstore = get_cached_connections()
    query_engine, _ = build_query_engine(st.session_state.credentials, embedding_model, llm, pinecone_index, docstore)
    agent = build_agent(st.session_state.credentials, query_engine, llm)
    return agent

def run_agent(agent, prompt):
    async def _run():
        if "agent_context" not in st.session_state:
            st.session_state.agent_context = Context(agent)

        return await agent.run(
            user_msg=prompt,
            ctx=st.session_state.agent_context
        )

    return asyncio.run(_run())

# @st.cache_resource
# def init_observability():
#     instrumentor = init_instrumentor(st.session_state.credentials)
#     instrumentor.start()
#     return instrumentor

def run_agent_with_status(agent, prompt):
    with st.status("*Reasoning about your question...*", expanded=True) as status:
        async def _run():
            if "agent_context" not in st.session_state:
                st.session_state.agent_context = Context(agent)
            handler = agent.run(
                user_msg=prompt,
                ctx=st.session_state.agent_context
            )

            tool_used = None
            async for event in handler.stream_events():
                evt_tool = getattr(event, "tool_name", None)
                if evt_tool:
                    tool_used = evt_tool
                    if tool_used == "aws_cli_command":
                        status.update(label=" Generating AWS CLI command...", state="running", expanded=True)
                    elif tool_used == "ec2_documentation_rag":
                        status.update(label=" Searching AWS EC2 documentation...", state="running", expanded=True)
            response = await handler

            if tool_used == "aws_cli_command":
                status.update(label=" Generated AWS CLI command", state="complete", expanded=True)
            elif tool_used == "ec2_documentation_rag":
                status.update(label=" Searched AWS EC2 documentation", state="complete", expanded=True)
            else:
                status.update(label=" Out of scope query", state="complete", expanded=True)
            return response
        return asyncio.run(_run())
    

st.set_page_config(page_title="EC2 Expert", page_icon="☁️")
st.title("AWS Technical Assistant for EC2")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "credentials" not in st.session_state:
    st.session_state.credentials = get_credentials("streamlit")

# init_observability()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.question_count >= MAX_REQUESTS:
    st.warning("⚠️ **Demostration limit reached.**")
    st.chat_input("Limit reached. Please try again later.", disabled=True)
elif prompt := st.chat_input("Ask me anything about EC2...", max_chars=120):
    st.session_state.question_count += 1
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    try:
        agent = load_rag_system()
        response_obj = run_agent_with_status(agent, prompt)
        response = str(response_obj)
    except Exception as e:
        if "429" in str(e):
            response = "⚠️ **Rate limit exceeded. Please try again later.**"
        elif "503" in str(e):
            response = "⚠️ **Service unavailable. The model is currently experiencing high demand. Please try again later.**"
        else:
            # traceback.print_exc()
            response = f"An error occurred while processing your query, I apologize for the inconvenience."
    with st.chat_message("assistant"):
        st.markdown(str(response))
    st.session_state.messages.append({"role": "assistant", "content": str(response)})