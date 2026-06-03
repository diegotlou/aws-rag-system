import time
import json
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.llms import ChatMessage
from utils.config import get_credentials
from utils.rag_system import build_connections, build_query_engine
from utils.read_local_data import read_local_data

API_DELAY = 5

def setup_components():
    credentials = get_credentials("env")
    pinecone_index, llm, docstore = build_connections(credentials)
    query_engine = build_query_engine(pinecone_index, llm, docstore)
    judge_client = GoogleGenAI(
        model=credentials.get("RAG_MODEL"),
        api_key=credentials.get("RAG_API_KEY"),
        temperature=0.0,
    )

    return query_engine, judge_client, credentials.get("RAG_MODEL"), credentials.get("JUDGE_MODEL") 

def load_evaluation_components(test_type):
    if test_type == 1 or test_type == 2:
        test_file = "judge_test_v1.jsonl"
        if test_type == 1:
            judge_file = "judge_faithfulness_prompt_v1.md"
            metric = "Faithfulness"
        else:
            judge_file = "judge_relevance_prompt_v1.md"
            metric = "Relevance"
    elif test_type == 3:
        test_file = "judge_test_robustness_v1.jsonl"
        judge_file = "judge_robustness_prompt_v1.md"
        metric = "Robustness"
    else:
        return
    test_cases = [json.loads(line) for line in read_local_data(test_file)]
    judge_prompt = read_local_data(judge_file)
    return test_cases, judge_prompt, metric, judge_file, test_file

def write_markdown_file(markdown_text, filename="evaluation_results.md"):
    with open(filename, "w", encoding='utf-8', errors='ignore') as f:
        f.write(markdown_text)

def evaluate_rag(test_cases, judge_prompt, metric, judge_file, test_file):
    query_engine, judge_client, rag_model_name, judge_model_name = setup_components()
    markdown_text = f"# Evaluación del sistema RAG para la prueba {metric}\n\n"
    markdown_text += f"* **Prompt:** {judge_file}\n* **RAG model:** {rag_model_name}\n* **JUDGE model:** {judge_model_name}\n* **Test:** {test_file}\n"
    print("Iniciando evaluacion del sistema RAG...")

    results = []
    for i, test in enumerate(test_cases):
        print(f"Evaluando caso de prueba {i+1}/{len(test_cases)}: {test['query']}")
        response_obj = query_engine.query(test["query"])
        time.sleep(API_DELAY)
        answer = str(response_obj)
        context_str = "\n\n".join([node.text for node in response_obj.source_nodes])
        
        evaluation_data = f"""
        USER QUERY: {test['query']}

        EXPECTED CORRECT CONCEPTS {test['expected_concept']}
        
        RETRIEVED CONTEXT:
        {context_str}
        
        SYSTEM ANSWER:
        {answer}
        """
        response = judge_client.chat(
            [
                ChatMessage(role="system", content=judge_prompt),
                ChatMessage(role="user", content=evaluation_data),
            ]
        )
        time.sleep(API_DELAY)
        json_response = json.loads(response.message.content)
        results.append(json_response["score"])

        markdown_text += f"## Caso de prueba {i+1}\n\n"
        markdown_text += f"**Pregunta de evaluación:**\n{test['query']}\n\n"
        markdown_text += f"**Respuesta del sistema RAG:**\n{answer}\n\n"
        markdown_text += f"**Evaluación del juez:**\n"
        json_keys = list(json_response.keys())
        for key in json_keys:
            print(f"- {key}: {json_response[key]}")
            markdown_text += f"- **{key}**: {json_response[key]}\n"
        markdown_text += "\n"

        time.sleep(API_DELAY)
    
    average_result = sum(r for r in results) / len(results)

    markdown_text += f"## Resultado final: {average_result}/5"
    print("\n" + "="*30)
    print(f"Resultado para {metric}: {average_result}/5")
    print("Para mas detalles, revise el documento de resultados completo.")
    write_markdown_file(markdown_text, filename=f"evaluation_results_{metric}.md")

if __name__ == "__main__":
    test_menu = "Ingrese el numero del test que desee ejecutar\n  1. Faithfulness\n  2. Relevance\n  3. Robustness\n"
    while True:
        test_type = int(input(test_menu))
        if test_type >= 1 and test_type <= 3 : break
        print(f"Ingrese una opcion valida\n{test_menu}")
    test_cases, judge_prompt, metric, judge_file, test_file = load_evaluation_components(test_type)
    evaluate_rag(test_cases, judge_prompt, metric, judge_file, test_file)
