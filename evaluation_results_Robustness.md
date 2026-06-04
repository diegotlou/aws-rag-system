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
I am sorry, but I cannot find that information in the EC2 documentation provided. I need more specific context to provide an answer.

**Evaluación del juez:**
- **inferred_intent**: The user wants to know why their EC2 instance is automatically restarting and how to prevent this behavior.
- **retrieval_assessment**: The retriever failed to find any documentation regarding EC2 auto-recovery or instance lifecycle behavior; it only returned code snippets for starting, stopping, and rebooting instances.
- **generation_assessment**: The generator correctly identified that the provided context did not contain the necessary information to answer the user's question.
- **failure_mode**: RETRIEVER_FAILURE
- **score**: 2
- **reasoning**: The retriever returned irrelevant code samples (API calls for stopping/starting instances) instead of conceptual documentation about EC2 auto-recovery. While the generator correctly admitted it couldn't answer, the system failed to provide the user with the actual solution to their problem due to poor retrieval.

## Caso de prueba 2

**Pregunta de evaluación:**
whats the cheapest way to run ec2 if i dont need it 24/7

**Respuesta del sistema RAG:**
To minimize costs for workloads that do not need to run 24/7, you can utilize the following options based on your specific requirements:

*   **Spot Instances:** This is a highly cost-effective choice if your applications are flexible about when they run and can handle interruptions. You can significantly reduce costs compared to On-Demand pricing. If your workload is "time-flexible," you can configure Spot Instances to stop or hibernate instead of terminating when interrupted.
*   **On-Demand Instances:** If your workload is irregular and cannot be interrupted, On-Demand Instances are suitable because there are no long-term commitments. You pay only for the seconds the instance is in a running state (with a 60-second minimum). Since you do not need the instance 24/7, you can stop the instance when it is not in use to avoid charges for usage or data transfer (though you will still be charged for EBS storage volumes).
*   **Burstable Performance Instances (T instances):** For workloads with low-to-moderate CPU utilization, T instances provide a cost-effective way to run general-purpose applications. If you use these in "unlimited" mode, be aware that you may incur charges for surplus credits if your average CPU usage exceeds the baseline over a 24-hour period. For short-duration Spot Instances, it is recommended to use "standard" mode to avoid these extra costs.
*   **Capacity Management:** If you require capacity for specific times, you can use Capacity Reservations to ensure availability in a specific Availability Zone.

**Important Considerations for Stopping Instances:**
*   **Billing:** When you stop an instance, you stop incurring charges for usage and data transfer. However, you are charged for a minimum of one minute of usage each time you start a stopped instance.
*   **Data:** Data on instance store volumes is lost when an instance is stopped or terminated. Ensure you back up important data to persistent storage like Amazon EBS, Amazon S3, or Amazon DynamoDB.

**Evaluación del juez:**
- **inferred_intent**: The user wants to know the most cost-effective ways to run EC2 instances for intermittent or part-time workloads.
- **retrieval_assessment**: The retriever successfully surfaced all relevant documentation, including Spot Instances, On-Demand stop/start behavior, and Burstable (T) instances.
- **generation_assessment**: The generator provided a highly specific, accurate, and well-structured answer that directly addressed the user's informal query by synthesizing the retrieved technical concepts.
- **failure_mode**: NONE
- **score**: 5
- **reasoning**: The system correctly interpreted the informal query and provided a comprehensive answer that covers the primary cost-saving mechanisms (Spot, stopping instances, and T-instances) while also including necessary caveats about data persistence and billing.

## Caso de prueba 3

**Pregunta de evaluación:**
I accidentally opened port 22 to everyone, is that bad and how do i close it

**Respuesta del sistema RAG:**
To close a port that you have opened in your security group, you must revoke the ingress rule. Based on the provided documentation, here is how you can manage your security group rules:

### How to remove an inbound rule
You can use the AWS CLI to revoke access to a specific port. While the documentation provides examples for revoking **egress** (outbound) rules, the process for managing security group rules generally involves identifying the specific rule and removing it.

If you are using the AWS CLI, you can use the `revoke-security-group-egress` command for outbound traffic, or the equivalent `authorize-security-group-ingress` logic to manage your inbound access. To specifically address your situation, you should verify your current security group rules and remove the rule that allows traffic on port 22 from `0.0.0.0/0`.

### Best Practices for SSH Access
The documentation indicates that for debugging or administrative access, it is standard practice to restrict SSH access (port 22) to your specific computer's IP address rather than opening it to everyone (`0.0.0.0/0`). 

*   **Verify your rules:** You can inspect your security group settings to see which IP ranges are currently allowed to access port 22.
*   **Restrict access:** When configuring your security group, ensure that the ingress rule for port 22 is limited to your specific IP address (e.g., `your-ip-address/32`) rather than a broad range.

If you are using tools like the AWS SDK or CLI, ensure you are using the appropriate commands to modify your security group ingress rules to reflect these tighter restrictions. If you need specific command syntax for your environment (such as PowerShell or a specific SDK), please refer to the `revoke` or `authorize` security group documentation provided in your AWS environment's specific CLI reference.

**Evaluación del juez:**
- **inferred_intent**: The user wants to know if exposing port 22 to the public (0.0.0.0/0) is a security risk and how to restrict that access to a specific IP address.
- **retrieval_assessment**: The retriever provided several code snippets related to security groups, including examples of adding/removing rules, but failed to provide a direct, clear command for revoking an *ingress* rule (it provided egress examples and ingress authorization examples).
- **generation_assessment**: The generator correctly identified the security risk and provided sound advice on best practices. However, it struggled to provide the exact CLI command for the user's specific problem (revoking an ingress rule), instead pointing to egress commands and general logic.
- **failure_mode**: GENERATOR_FAILURE
- **score**: 3
- **reasoning**: The system correctly identified the intent and the security risk. However, it failed to provide the specific command needed (revoke-security-group-ingress), instead providing an egress command and general guidance. The user would still need to look up the correct syntax for the ingress revocation.

## Caso de prueba 4

**Pregunta de evaluación:**
can i move my ec2 to a different region or do i have to start over

**Respuesta del sistema RAG:**
You can move your EC2 instance configuration to a different region by using an Amazon Machine Image (AMI) as a template. Because AMIs are region-specific resources, you must copy the AMI from your source region to your target region.

Here is the general process for moving your configuration:

1.  **Create an AMI:** Create an AMI from your existing EC2 instance. This captures the configuration of your instance.
2.  **Copy the AMI:** Copy the AMI from the source region to the desired target region. You can perform this copy using the Amazon EC2 console, the AWS CLI (`aws ec2 copy-image`), or PowerShell (`Copy-EC2Image`).
3.  **Launch in the new region:** Once the copy is complete and available in the target region, you can use that AMI to launch new instances in that region with the same configuration.

**Important Considerations:**
*   **Timeframe:** The copy operation is performed on a best-effort basis. If you need to ensure the copy completes within a specific timeframe, you can specify a completion window ranging from 15 minutes to 48 hours.
*   **Data Migration:** If you have data on instance store volumes, you must copy that data to persistent storage (such as EBS volumes) before creating the AMI, as instance store data is not preserved in the AMI.
*   **Elastic IP Addresses:** Elastic IP addresses are region-specific and cannot be moved directly. If your original instance uses one, you will need to associate a new Elastic IP address with your instance in the target region.

**Evaluación del juez:**
- **inferred_intent**: The user wants to know if they can migrate an existing EC2 instance to a different AWS region and what the procedure is.
- **retrieval_assessment**: The retriever successfully identified multiple relevant sections of the documentation, including instructions for copying AMIs and the general migration process.
- **generation_assessment**: The generator provided a clear, accurate, and step-by-step response that directly addresses the user's binary question by explaining the AMI-based migration process.
- **failure_mode**: NONE
- **score**: 5
- **reasoning**: The system correctly interpreted the informal query, retrieved highly relevant documentation, and synthesized a comprehensive answer that explains the process while clarifying the limitations (e.g., Elastic IPs, instance store data).

## Resultado final: 3.75/5