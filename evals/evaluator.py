import os
from dotenv import load_dotenv
import json
from pinecone import Pinecone
from groq import Groq
from utils.rag_system import build_query_engine
from utils.read_local_data import read_local_data

load_dotenv()
JUDGE_API_KEY = os.environ.get("JUDGE_API_KEY")
TEST_CASES = [json.loads(line) for line in read_local_data("judge_test_v1.jsonl")]
JUDGE_PROMPT = read_local_data("judge_v1.md")

judge_client = Groq(api_key=JUDGE_API_KEY)

def write_markdown_file(markdown_text, filename="evaluation_results.md"):
    with open(filename, "w") as f:
        f.write(markdown_text)

def evaluate_rag():
    markdown_text = "# Evaluación del sistema RAG para AWS EC2\n\n"
    print("Iniciando evaluación del sistema RAG...")
    pinecone = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    pinecone_index = pinecone.Index(host=os.environ.get("PINECONE_HOST"))
    system_prompt = read_local_data("system_prompt_v1.md")
    llm = Groq(
        model="llama-3.3-70b-versatile", 
        api_key=os.environ.get("GROQ_API_KEY"),
        system_prompt=system_prompt
    )
    query_engine = build_query_engine(pinecone_index, llm)

    results = []
    for i, test in enumerate(TEST_CASES):
        print(f"Evaluando caso de prueba {i+1}/{len(TEST_CASES)}: {test['query']}")
        response_obj = query_engine.query(test["query"])
        
        answer = str(response_obj)
        context_str = "\n\n".join([node.text for node in response_obj.source_nodes])
        
        evaluation_data = f"""
        USER QUERY: {test['query']}
        
        RETRIEVED CONTEXT:
        {context_str}
        
        SYSTEM ANSWER:
        {answer}
        """

        chat_completion = judge_client.chat.completions.create(
            messages=[
                { "role": "system", "content": JUDGE_PROMPT},
                { "role": "user", "content": evaluation_data}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.0
        )

        json_response = json.loads(chat_completion.choices[0].message.content)
        results.append(json_response)

        markdown_text += f"## Caso de prueba {i+1}\n\n"
        markdown_text += f"**Pregunta de evaluación:**\n{test['query']}\n\n"
        markdown_text += f"**Respuesta del sistema RAG:**\n{answer}\n\n"
        markdown_text += f"**Evaluación del juez:**\n"
        markdown_text += f"- Fidelidad: {json_response['faithfulness_score']}/5\n"
        markdown_text += f"  - Razonamiento: {json_response['faithfulness_reasoning']}\n"
        markdown_text += f"- Relevancia: {json_response['relevance_score']}/5\n"
        markdown_text += f"  - Razonamiento: {json_response['relevance_reasoning']}\n\n"
    
    average_faithfulness = sum(r['faithfulness_score'] for r in results) / len(results)
    average_relevance = sum(r['relevance_score'] for r in results) / len(results)

    markdown_text += f"## Resultados finales\n\n"
    markdown_text += f"- Promedio de fidelidad: {average_faithfulness}/5\n"
    markdown_text += f"- Promedio de relevancia: {average_relevance}/5\n\n"
    print("\n" + "="*30)
    print(f"Resultados finales:")
    print(f"Promedio de fidelidad: {average_faithfulness}/5")
    print(f"Promedio de relevancia: {average_relevance}/5")
    print("Para mas detalles, revise el documento de resultados completo.")
    write_markdown_file(markdown_text)

if __name__ == "__main__":
    evaluate_rag()
