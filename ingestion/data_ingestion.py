import os
from pinecone import Pinecone
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.readers.file import PyMuPDFReader
from dotenv import load_dotenv

load_dotenv()

def load_documents(target_path):
    if not os.path.exists(target_path):
        print(f"Error: El path '{target_path}' no existe.")
        return

    # Configura el extractor para PDFs usando PyMuPDFReader
    parser = PyMuPDFReader()
    file_extractor = {".pdf": parser}

    print(f"Cargando documentos desde {target_path}...")
    # Usa el extractor al SimpleDirectoryReader
    docs = SimpleDirectoryReader(target_path, file_extractor=file_extractor).load_data()

    category = os.path.basename(target_path.strip("/"))  # Extrae el nombre de la carpeta como categoría
    
    sensitive_metadata = [
        "file_path", 
        "creation_date", 
        "last_modified_date", 
        "last_accessed_date"
    ]
    
    for doc in docs:
        doc.metadata["category"] = category

        for metadata in sensitive_metadata:
            doc.metadata.pop(metadata, None)

    return docs

def setup_components():
    # Inicializa el modelo de HuggingFaceEmbeddings, el hierarchical parser, el vector store y docstore
    pinecone = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    pinecone_index = pinecone.Index(host=os.environ.get("PINECONE_HOST"))

    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    docstore = MongoDocumentStore.from_uri(
        uri=os.environ.get("MONGO_DB_URI"),
        db_name=os.environ.get("MONGO_DB_NAME"),
        namespace=os.environ.get("MONGO_DB_NAMESPACE")
    )
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[2048, 512])

    return vector_store, embed_model, node_parser, docstore

def ingest_folder(target_path):
    # Carga y categoriza los documentos desde la carpeta especificada por el usuario
    docs = load_documents(target_path)
    if not docs : return

    # Configura los componentes necesarios para el procesamiento de documentos
    vector_store, embed_model, node_parser, docstore = setup_components()
    
    # Procesa los documentos para obtener los nodos y luego los nodos hoja
    print("Fragmentando documentos (Chunking)...")
    nodes = node_parser.get_nodes_from_documents(docs)
    leaf_nodes = get_leaf_nodes(nodes)

    # Crea el Storage Context con el vector store y docstore
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore
    )

    print(f"Subiendo datos a MongoDB Atlas...")
    storage_context.docstore.add_documents(nodes)

    # Indexa los nodos hoja en Pinecone
    print(f"Indexando {len(leaf_nodes)} nodos hoja en Pinecone...")
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store, 
        embed_model=embed_model,
        storage_context=storage_context
    )
    # Insertamos los nuevos nodos 
    index.insert_nodes(leaf_nodes)

    print("Ingesta completada!")

if __name__ == "__main__":
    # El usuario introduce la ruta a su directorio de documentos.
    target_path = input("Introduce la ruta de la carpeta de documentos: ")
    ingest_folder(target_path)