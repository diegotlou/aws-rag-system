import os
import streamlit as st
from pinecone import Pinecone
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.readers.file import PyMuPDFReader

DOCSTORE_PATH = "./data/local_docstore.json"

def load_documents(target_path):
    if not os.path.exists(target_path):
        print(f"Error: El path '{target_path}' no existe.")
        return

    # Configura el extractor para PDFs usando PyMuPDFReader
    parser = PyMuPDFReader()
    file_extractor = {".pdf": parser}

    # Usa el extractor al SimpleDirectoryReader
    docs = SimpleDirectoryReader(target_path, file_extractor=file_extractor).load_data()

    category = os.path.basename(target_path.split("/")[-1])  # Extrae el nombre de la carpeta como categoría
    for doc in docs:
        doc.metadata["category"] = category

    return docs

def setup_components():
    # Inicializa el modelo de HuggingFaceEmbeddings, el hierarchical parser, el vector store y docstore
    pinecone = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    pinecone_index = pinecone.Index(host=st.secrets["PINECONE_HOST"])
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    # Reducimos a dos niveles para reducir el tamaño de local_docstore.json
    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[2048, 512])
    
    if os.path.exists(DOCSTORE_PATH):
        print("Cargando docstore existente...")
        docstore = SimpleDocumentStore.from_persist_path(DOCSTORE_PATH)
    else:
        print("Creando nuevo docstore...")
        docstore = SimpleDocumentStore()

    return vector_store, embed_model, node_parser, docstore

def ingest_folder(target_path):
    # Carga y categoriza los documentos desde la carpeta especificada por el usuario
    docs = load_documents(target_path)

    # Configura los componentes necesarios para el procesamiento de documentos
    vector_store, embed_model, node_parser, docstore = setup_components()
    
    # Procesa los documentos para obtener los nodos y luego los nodos hoja
    nodes = node_parser.get_nodes_from_documents(docs)
    leaf_nodes = get_leaf_nodes(nodes)

    # Crea el Storage Context con el vector store y docstore, y agregamos los nodos al docstore local
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore
    )
    storage_context.docstore.add_documents(nodes)

    # Indexa los nodos hoja en Pinecone
    print(f"Indexando {len(leaf_nodes)} nodos hoja en Pinecone...")
    VectorStoreIndex(
        leaf_nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        insert_batch_size=100
    )

    # Guarda el docstore localmente para futuras cargas
    storage_context.docstore.persist(persist_path=DOCSTORE_PATH)
    print("Indexación completada y docstore guardado localmente.")

if __name__ == "__main__":
    # El usuario introduce la ruta a su directorio de documentos.
    target_path = input("Introduce la ruta de la carpeta de documentos: ")
    ingest_folder(target_path)