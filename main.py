import streamlit as st
from pinecone import Pinecone
from llama_index.llms.groq import Groq
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from utils.read_local_data import read_local_data
from utils.rag_system import build_query_engine

@st.cache_resource
def load_rag_system():
    # Configura la conexión a Pinecone y carga el modelo de lenguaje y el modelo de embeddings
    pinecone = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    pinecone_index = pinecone.Index(host=st.secrets["PINECONE_HOST"])
    system_prompt = read_local_data("system_prompt_v1.md")
    llm = Groq(
        model="llama-3.3-70b-versatile", 
        api_key=st.secrets["GROQ_API_KEY"],
        system_prompt=system_prompt
    )
    docstore = MongoDocumentStore.from_uri(
        uri=st.secrets["MONGO_DB_URI"],
        db_name=st.secrets["MONGO_DB_NAME"],
        namespace=st.secrets["MONGO_DB_NAMESPACE"]
    )
    query_engine = build_query_engine(pinecone_index, llm, docstore)
    return query_engine

st.set_page_config(page_title="EC2 Expert", page_icon="☁️")
st.title("AWS Technical Assistant for EC2")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about EC2..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    try:
        query_engine = load_rag_system()
        response = query_engine.query(prompt)
    except Exception as e:
        response = f"An error occurred while processing your query: {str(e)}"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})