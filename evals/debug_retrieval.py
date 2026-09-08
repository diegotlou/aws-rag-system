from utils.rag_system import build_query_engine
from utils.config import get_credentials

def debug_retrieval(retriever, query):
    nodes = retriever.retrieve(query)

    print("\n" + "=" * 20)
    print(f"QUERY: {query}")
    print("=" * 20)

    for idx, node in enumerate(nodes, 1):
        print(f"\nRESULT {idx}")
        print(f"Score: {getattr(node, 'score', 'N/A')}")
        print(f"Metadata: {node.metadata}")
        print(node.text[:2000])
        print("-" * 100)

    return nodes

if __name__ == "__main__":
    credentials = get_credentials("env")
    _, base_query_engine = build_query_engine(credentials)
    query = input("Input the query:\n")
    debug_retrieval(base_query_engine, query)