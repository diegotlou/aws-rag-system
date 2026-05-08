import os
from dotenv import load_dotenv
import json
from groq import Groq
from main import load_rag_system

load_dotenv()
JUDGE_API_KEY = os.getenv("JUDGE_API_KEY")

TEST_CASES = [
    {
        "query": "What are the steps to launch an EC2 instance using the AWS Management Console?",
        "expected_concept": "Step-by-step instructions using the AWS Console: selecting an AMI, choosing an instance type, configuring network settings, adding storage, configuring security groups, and launching the instance."
    },
    {
        "query": "What is the difference between On-Demand, Reserved, and Spot Instances in EC2?",
        "expected_concept": "Explanation of the three EC2 pricing models: On-Demand (pay per use), Reserved Instances (commitment for lower cost), and Spot Instances (bid on unused capacity at a discount)."
    },
    {
        "query": "How does EC2 handle idempotency in API requests?",
        "expected_concept": "Description of how EC2 uses client tokens to ensure that repeated API requests (e.g., RunInstances) produce the same result without duplicating resources."
    },
    {
        "query": "What is an Amazon Machine Image (AMI) and what are its key characteristics?",
        "expected_concept": "Definition of AMI as a template containing the OS and application configuration. Key characteristics include launch permissions, root volume type, and virtualization type."
    },
    {
        "query": "How do security groups work in Amazon EC2?",
        "expected_concept": "Security groups act as virtual firewalls controlling inbound and outbound traffic for EC2 instances, with rules based on protocol, port, and source/destination IP."
    },
    {
        "query": "What is EC2 API request throttling and how should developers handle it?",
        "expected_concept": "Explanation of how EC2 throttles API requests when limits are exceeded, and recommended strategies like exponential backoff and retries to handle throttling gracefully."
    },
    {
        "query": "How can I connect to my EC2 instance after launching it?",
        "expected_concept": "Methods to connect to an EC2 instance, including SSH for Linux using a key pair, and RDP for Windows instances, with details on obtaining the public DNS or IP address."
    },
    {
        "query": "What are EC2 placement groups and when should I use each strategy?",
        "expected_concept": "Overview of the three placement group strategies: Cluster (low latency, high throughput), Spread (high availability across hardware), and Partition (large distributed workloads like Hadoop/Cassandra)."
    },
    {
        "query": "How do I use the AWS SDK or CLI to programmatically manage EC2 resources?",
        "expected_concept": "Description of using AWS SDKs and the AWS CLI to interact with EC2 via the API, including code examples for common operations like launching and describing instances."
    },
    {
        "query": "What is the role of Elastic IP addresses in EC2 and how are they used?",
        "expected_concept": "Elastic IPs are static public IPv4 addresses that can be associated with EC2 instances or network interfaces, allowing a fixed IP even if the instance is stopped or restarted."
    },
    {
        "query": "How do IAM roles work with EC2 instances for secure access to AWS services?",
        "expected_concept": "IAM roles can be attached to EC2 instances to grant permissions to access other AWS services without embedding access keys, following the principle of least privilege."
    },
    {
        "query": "What are the best practices for securing an EC2 instance?",
        "expected_concept": "Best practices including using IAM roles instead of access keys, restricting security group rules, keeping the OS patched, using key pairs for SSH, and enabling detailed monitoring."
    },
    {
        "query": "How does EBS (Elastic Block Store) integrate with EC2 and what are its volume types?",
        "expected_concept": "EBS provides persistent block storage for EC2 instances. Volume types include General Purpose SSD (gp2/gp3), Provisioned IOPS SSD (io1/io2), and Throughput Optimized HDD (st1)."
    },
    {
        "query": "What is eventual consistency in EC2 and how can it affect API operations?",
        "expected_concept": "Explanation that EC2 uses an eventually consistent model for reads after writes, meaning a newly created resource may not be immediately visible in subsequent describe calls, and guidance on how to handle this in code."
    },
    {
        "query": "How can I monitor EC2 API usage and set up CloudWatch alarms for throttling events?",
        "expected_concept": "Steps to enable EC2 API metrics in CloudWatch, including available metrics and dimensions, and how to create alarms to detect and respond to API throttling or high request rates."
    }
]

JUDGE_PROMPT = """
You are an impartial AI judge evaluating a RAG (Retrieval-Augmented Generation) system.
You will be provided with a User Query, the Context retrieved from the database, and the System's Answer.

You must evaluate two metrics on a scale of 1 to 5:
1. FAITHFULNESS: Is the System's Answer strictly based on the Context? (1 = Hallucinated/Not in context, 5 = Perfectly grounded in context).
2. RELEVANCE: Does the System's Answer directly address the User Query? (1 = Completely irrelevant, 5 = Perfectly answers the query).

Return ONLY a valid JSON object with this exact structure:
{
    "faithfulness_score": <int>,
    "faithfulness_reasoning": "<brief explanation>",
    "relevance_score": <int>,
    "relevance_reasoning": "<brief explanation>"
}
"""

judge_client = Groq(api_key=JUDGE_API_KEY)

def write_markdown_file(markdown_text, filename="evaluation_results.md"):
    with open(filename, "w") as f:
        f.write(markdown_text)

def evaluate_rag():
    markdown_text = "# Evaluación del sistema RAG para AWS EC2\n\n"
    print("Iniciando evaluación del sistema RAG...")
    query_engine = load_rag_system()

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
