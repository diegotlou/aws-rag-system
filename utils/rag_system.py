from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine, TransformQueryEngine
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from utils.read_local_data import read_local_data

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

def get_emebedding_model(token):
    return HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME, token=token)

def get_llm(credentials, system_prompt=None):
    from llama_index.llms.google_genai import GoogleGenAI

    if system_prompt is None : system_prompt = read_local_data("system_prompt_v3.md")

    llm = GoogleGenAI(
        model=credentials.get("RAG_MODEL"),
        api_key=credentials.get("RAG_API_KEY"),
        system_prompt=system_prompt,
        temperature=0.2
    )
    return llm

def build_connections(credentials):
    from pinecone import Pinecone
    from llama_index.storage.docstore.mongodb import MongoDocumentStore

    # Conexion a Pinecone
    pinecone = Pinecone(api_key=credentials.get("PINECONE_API_KEY"))
    pinecone_index = pinecone.Index(host=credentials.get("PINECONE_HOST"))
    # Conexion a MongoDB
    docstore = MongoDocumentStore.from_uri(
        uri=credentials.get("MONGO_DB_URI"),
        db_name=credentials.get("MONGO_DB_NAME"),
        namespace=credentials.get("MONGO_DB_NAMESPACE")
    )
    
    return pinecone_index, docstore

def build_query_engine(credentials, embedding_model=None, llm=None, pinecone_index=None, docstore=None):
    if embedding_model is None : embedding_model = get_emebedding_model()
    if llm is None : llm = get_llm(credentials)
    if pinecone_index is None and docstore is None: pinecone_index, docstore = build_connections(credentials)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    # Crea el contexto de almacenamiento
    storage_context = StorageContext.from_defaults(vector_store=vector_store, docstore=docstore)

    # Crea el indice base, retriever y query engine
    base_index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embedding_model)
    base_retriever = base_index.as_retriever(similarity_top_k=12)
    retriever = AutoMergingRetriever(base_retriever, storage_context)

    qa_prompt_str = read_local_data("qa_prompt_v3.md")
    qa_prompt_template = PromptTemplate(qa_prompt_str)

    base_query_engine = RetrieverQueryEngine.from_args(retriever, llm, response_mode="compact")
    base_query_engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt_template})

    hyde = HyDEQueryTransform(include_original=True, llm=llm)
    query_engine = TransformQueryEngine(base_query_engine, query_transform=hyde)
    
    return query_engine, base_query_engine