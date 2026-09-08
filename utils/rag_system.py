from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine, TransformQueryEngine
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from utils.read_local_data import read_local_data
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.agent.workflow import ReActAgent

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

def build_agent(credentials, query_engine=None, llm=None):
    if llm is None : llm = get_llm(credentials)
    if query_engine is None : query_engine = build_query_engine(credentials, llm=llm)[0]

    # Tool 1: Motor RAG (búsqueda semántica)
    rag_tool = QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="ec2_documentation_rag",
            description=(
                "Use this tool to answer questions about AWS EC2 "
                "using the provided technical documentation. "
                "Use it for explanations, concepts, configuration, "
                "troubleshooting and questions about how EC2 works."
            )
        )
    )

    # Tool 2: Generador de AWS CLI
    def generate_aws_cli(command_request: str) -> str:
        """
        Generate only an AWS CLI command for the requested EC2 operation.
        """
        prompt = f"""
Generate the AWS CLI command required to perform the following request.

Rules:
- Return ONLY the AWS CLI command.
- Do not explain the command.
- Do not use Markdown.
- Do not include multiple commands.
- Do not try to execute the command.
- Prefer the AWS CLI v2 syntax.
- If the request cannot be represented safely as a single AWS CLI command,
  return: UNSUPPORTED

Request:
{command_request}
"""
        response = llm.complete(prompt)
        return str(response).strip()

    cli_tool = FunctionTool.from_defaults(
        fn=generate_aws_cli,
        name="aws_cli_command",
        description=(
            "Use this tool ONLY when the user asks for an AWS CLI command "
            "to perform an EC2 operation. This tool generates commands but "
            "does not execute them."
        )
    )

    agent_system_prompt = (
        "You are a specialized AWS EC2 AI Assistant.\n"
        "Your ONLY focus is AWS EC2 documentation and AWS CLI commands for EC2.\n\n"
        "STRICT ROUTING RULES:\n"
        "1. If the user asks theoretical questions, concepts, or technical troubleshooting about AWS EC2, "
        "you MUST call the `ec2_documentation_rag` tool.\n"
        "2. If the user requests an AWS CLI command for EC2, you MUST call the `aws_cli_command` tool.\n"
        "3. For ANY question unrelated to AWS EC2 (e.g., Slack installation, general OS questions, non-AWS topics), "
        "DO NOT CALL ANY TOOLS. Immediately reply with: 'I am a specialized AWS EC2 Assistant. "
        "I can only help with AWS EC2 technical documentation and AWS CLI commands for EC2.'"
    )

    agent = ReActAgent(
        name="aws_ec2_agent",
        tools=[rag_tool, cli_tool],
        llm=llm,
        system_prompt=agent_system_prompt
    )

    return agent