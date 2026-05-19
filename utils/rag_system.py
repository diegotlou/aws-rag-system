from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from utils.read_local_data import read_local_data

def build_query_engine(pinecone_index, llm, docstore):
    # Configura la conexión a Pinecone y carga el modelo de lenguaje y el modelo de embeddings
    embedding_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Conecta al vector store de Pinecone
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    # Crea el contexto de almacenamiento
    storage_context = StorageContext.from_defaults(vector_store=vector_store, docstore=docstore)
    
    # Crea el índice base, retriever y query engine
    base_index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embedding_model)
    base_retriever = base_index.as_retriever(similarity_top_k=12)
    retriever = AutoMergingRetriever(base_retriever, storage_context)

    qa_prompt_str = read_local_data("qa_prompt_v1.md")
    qa_prompt_template = PromptTemplate(qa_prompt_str)

    query_engine = RetrieverQueryEngine.from_args(retriever, llm)
    query_engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt_template})
    
    return query_engine