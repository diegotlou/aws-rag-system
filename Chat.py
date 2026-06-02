import streamlit as st
from utils.config import get_credentials
from utils.rag_system import get_emebedding_model, build_connections, build_query_engine

MAX_REQUESTS = 5

@st.cache_resource
def _load_embedding_model():
    return get_emebedding_model()

@st.cache_resource
def load_rag_system():
    credentials = get_credentials(source="streamlit")
    pinecone_index, llm, docstore = build_connections(credentials)
    embedding_model = _load_embedding_model()
    return build_query_engine(pinecone_index, llm, docstore, embedding_model)

st.set_page_config(page_title="EC2 Expert", page_icon="☁️")
st.title("AWS Technical Assistant for EC2")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

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