import streamlit as st
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, PromptTemplate
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine


@st.cache_resource
def load_rag_system():
    # Configura la conexión a Pinecone y carga el modelo de lenguaje y el modelo de embeddings
    pinecone = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    pinecone_index = pinecone.Index(host=st.secrets["PINECONE_HOST"])
    llm = Groq(
        model="llama-3.3-70b-versatile", 
        api_key=st.secrets["GROQ_API_KEY"],
        system_prompt=(
            "You are an expert AWS Technical Assistant specialized in EC2. "
            "Your job is to answer user questions based STRICTLY on the provided context. "
            "CRITICAL RULES: "
            "1. NEVER output PDF raw code, binary strings, or terms like 'endstream', 'endobj', or 'object ID'. "
            "2. NEVER reference section titles, object numbers, or tell the user to 'go to a section' or 'read the tutorial'. "
            "3. You must extract the actual steps or concepts and explain them directly to the user. "
            "4. If the provided context only contains titles or index pages, respond: 'I need more specific context to provide the exact steps.' "
            "If the answer is not contained in the context, do not guess."
            "Simply reply: 'I am sorry, but I cannot find that information in the EC2 documentation provided.'"
        )
    )
    embedding_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Conecta al vector store de Pinecone
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    # Carga los documentos en el docstore
    docstore = SimpleDocumentStore.from_persist_path("./data/local_docstore.json")

    # Crea el contexto de almacenamiento
    storage_context = StorageContext.from_defaults(vector_store=vector_store, docstore=docstore)
    
    # Crea el índice base, retriever y query engine
    base_index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embedding_model)
    base_retriever = base_index.as_retriever(similarity_top_k=12)
    retriever = AutoMergingRetriever(base_retriever, storage_context)

    qa_prompt_str = (
        "Context information from AWS documentation is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information and not prior knowledge, answer the query.\n"
        "Query: {query_str}\n"
        "Answer: "
    )

    qa_prompt_template = PromptTemplate(qa_prompt_str)

    query_engine = RetrieverQueryEngine.from_args(retriever, llm)
    query_engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt_template})
    
    return query_engine


if __name__ == "__main__":
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