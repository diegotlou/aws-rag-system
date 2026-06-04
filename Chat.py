import streamlit as st
from utils.config import get_credentials
from utils.read_local_data import read_local_data
from utils.rag_system import get_emebedding_model, get_llm, build_connections, build_query_engine

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
    return query_engine

st.set_page_config(page_title="EC2 Expert", page_icon="☁️")
st.title("AWS Technical Assistant for EC2")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "credentials" not in st.session_state:
    st.session_state.credentials = get_credentials("streamlit")

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
        query_engine = load_rag_system()
        with st.spinner("Analyzing technical documentation..."):
            response = query_engine.query(prompt)
    except Exception as e:
        if "429" in str(e):
            response = "⚠️ **Rate limit exceeded. Please try again later.**"
        else:
            response = f"An error occurred while processing your query, I apologize for the inconvenience."
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})