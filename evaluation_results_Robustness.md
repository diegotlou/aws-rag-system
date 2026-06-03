# Evaluación del sistema RAG para la prueba Robustness

* **System Prompt:** system_prompt_v3.md
* **QA Prompt:** qa_prompt_v3.md
* **Judge Prompt:** judge_robustness_prompt_v1.md
* **RAG model:** gemini-3.1-flash-lite
* **JUDGE model:** gemini-3.1-flash-lite
* **Test:** judge_test_robustness_v1.jsonl
## Caso de prueba 1

**Pregunta de evaluación:**
my server keeps restarting by itself, how do i stop that??

**Respuesta del sistema RAG:**
I am sorry, but I cannot find that information in the EC2 documentation provided.

**Evaluación del juez:**
- **inferred_intent**: The user wants to know why their EC2 instance is automatically restarting and how to prevent this behavior.
- **retrieval_assessment**: The retriever failed to find relevant documentation regarding EC2 auto-recovery or instance shutdown behavior. It returned code snippets for starting, stopping, and rebooting instances, which are irrelevant to the user's troubleshooting question.
- **generation_assessment**: The generator correctly identified that the provided context did not contain the answer, but it failed to provide any helpful guidance or general knowledge about EC2 auto-recovery, resulting in a dead-end response.
- **failure_mode**: BOTH
- **score**: 1
- **reasoning**: The retriever returned code examples for programmatic instance management instead of conceptual documentation about instance lifecycle and auto-recovery. Consequently, the generator could not answer the question, leading to a complete failure to assist the user.

## Caso de prueba 2

**Pregunta de evaluación:**
whats the cheapest way to run ec2 if i dont need it 24/7

**Respuesta del sistema RAG:**
To minimize costs for workloads that do not need to run 24/7, you can utilize several Amazon EC2 purchasing options and management strategies based on your specific needs:

*   **Spot Instances:** These are the most cost-effective choice if your applications are flexible about when they run and can handle interruptions. You can significantly reduce costs compared to On-Demand pricing.
*   **Stop and Start:** Since you do not need your instances running 24/7, you can stop them when they are not in use. You are not charged for usage or data transfer fees while an instance is in the stopped state (though you are still charged for Amazon EBS storage volumes). 
    *   *Note:* When you stop an instance, any data on instance store volumes is lost.
    *   *Billing:* You are charged for a minimum of one minute each time you start an instance. After the first minute, you are charged per second.
*   **Savings Plans:** If you can commit to a specific amount of usage (measured in $/hour) rather than a specific instance configuration, you can purchase Savings Plans to reduce your On-Demand Instance costs.
*   **Capacity Reservations:** If you require guaranteed capacity in a specific Availability Zone, you can use Capacity Reservations or Reserved Instances.
*   **Fleet Management:** If you are running a fleet of instances, using an **EC2 Fleet** or **Amazon EC2 Auto Scaling** allows you to combine Spot and On-Demand instances to optimize costs. Auto Scaling is generally recommended as it provides additional features like automatic health checks and integration with Elastic Load Balancing.

**Best Practices for Cost Optimization:**
*   **Be Flexible:** When using Spot Instances, be flexible across multiple instance types and Availability Zones to increase the likelihood of finding available capacity.
*   **Use Appropriate Allocation Strategies:** When using fleets, use the `price-capacity-optimized` allocation strategy to source instances from the most available and lowest-priced pools, which also reduces the risk of interruption.
*   **Prepare for Interruptions:** If using Spot Instances, ensure your application is fault-tolerant by using checkpoints, backing up data to persistent storage (like Amazon S3 or EBS), and monitoring for rebalance recommendations or interruption notices.

**Evaluación del juez:**
- **inferred_intent**: The user wants to know the most cost-effective ways to run EC2 instances for non-continuous (part-time) workloads.
- **retrieval_assessment**: The retriever successfully surfaced all relevant documentation regarding Spot Instances, the stop/start lifecycle, and general cost-optimization strategies.
- **generation_assessment**: The generator provided a highly specific, accurate, and well-structured answer that directly addressed the user's informal query by mapping it to the correct technical concepts.
- **failure_mode**: NONE
- **score**: 5
- **reasoning**: The system correctly interpreted the informal query and synthesized the retrieved technical documentation into a clear, actionable response that covers both the 'stop/start' approach and the 'Spot Instance' approach for cost savings.

## Caso de prueba 3

**Pregunta de evaluación:**
I accidentally opened port 22 to everyone, is that bad and how do i close it

**Respuesta del sistema RAG:**
Yes, opening port 22 (SSH) to everyone (0.0.0.0/0) is a security risk. AWS documentation strongly recommends that you authorize only the specific IP address or range of addresses that require access to your instances.

To restrict access and close port 22 to the public, follow these steps using the Amazon EC2 console:

1.  Open the **Amazon EC2 console** at https://console.aws.amazon.com/ec2/.
2.  In the navigation pane, choose **Security Groups**.
3.  Select the security group associated with your instance.
4.  Locate the inbound rule that allows SSH (port 22) traffic.
5.  Modify the rule to restrict the source. Instead of "Anywhere-IPv4" (0.0.0.0/0), change the source to **"My IP"** (which automatically detects your computer's public IPv4 address) or specify the exact IP address/range that needs access.
6.  Save the changes to the security group.

By limiting the source to your specific IP address, you ensure that only your computer can attempt to connect to your instance via SSH.

**Evaluación del juez:**
- **inferred_intent**: The user wants to know if exposing port 22 to the public is a security risk and how to restrict access to that port in their AWS security group.
- **retrieval_assessment**: The retriever successfully surfaced highly relevant documentation, specifically the section detailing security group configuration, the warning about port 22, and the 'My IP' restriction method.
- **generation_assessment**: The generator provided a clear, accurate, and actionable response that directly addressed both parts of the user's query using the retrieved context.
- **failure_mode**: NONE
- **score**: 5
- **reasoning**: The system correctly identified the security implications of the user's action and provided precise, step-by-step instructions to remediate the issue using the AWS console, despite the informal nature of the query.

## Caso de prueba 4

**Pregunta de evaluación:**
can i move my ec2 to a different region or do i have to start over

**Respuesta del sistema RAG:**
You do not necessarily have to start over. Because Amazon Machine Images (AMIs) are Region-specific resources, you can move your configuration to a different Region by copying the AMI.

Here is how you can handle this process:

### Copying an AMI to a different Region
You can copy an AMI from your source Region to a target Region, which allows you to launch consistent instances in the new location. You can perform this using the AWS Management Console or the AWS CLI:

*   **Using the Console:**
    1.  Navigate to the EC2 console and select the Region containing your AMI.
    2.  In the navigation pane, choose **AMIs**.
    3.  Select the desired AMI, then choose **Actions** > **Copy AMI**.
    4.  Specify the **Destination Region** and other configuration details (such as a name and description), then complete the copy.

*   **Using the AWS CLI:**
    Use the `copy-image` command, specifying the source Region and the destination Region:
    ```bash
    aws ec2 copy-image \
        --source-image-id ami-0abcdef1234567890 \
        --source-region us-west-2 \
        --name my-ami \
        --region us-east-1
    ```

### Important Considerations
*   **Application Configuration:** Before copying, ensure the contents of the source AMI are updated to support the new Region. For example, you should update database connection strings or application configuration data to point to resources in the destination Region to avoid performance or cost issues.
*   **Time-based Copying:** The time taken to copy an AMI is on a best-effort basis. If you require the copy to finish within a specific timeframe, you can specify a completion window ranging from 15 minutes to 48 hours.
*   **Limitations:** You cannot copy a paravirtual (PV) AMI to a Region that does not support PV AMIs. Additionally, there is a limit of 300 concurrent AMI copy operations per destination Region.
*   **Encryption:** If you are copying an encrypted AMI, you must specify the `--encrypted` and `--kms-key-id` parameters.

**Evaluación del juez:**
- **inferred_intent**: The user wants to know if they can migrate an existing EC2 instance to a different AWS region and what the process is.
- **retrieval_assessment**: The retriever successfully identified the relevant documentation regarding AMI copying, which is the standard mechanism for cross-region migration.
- **generation_assessment**: The generator provided a clear, accurate, and actionable response that directly addressed the user's binary question and provided the necessary technical steps.
- **failure_mode**: NONE
- **score**: 5
- **reasoning**: The system correctly interpreted the informal query, retrieved the exact documentation needed to explain the migration process (AMI copying), and synthesized a helpful, step-by-step guide that clarifies that the user does not need to 'start over' from scratch.

## Resultado final: 4.0/5