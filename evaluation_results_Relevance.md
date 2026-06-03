# Evaluación del sistema RAG para la prueba Relevance

* **System Prompt:** system_prompt_v3.md
* **QA Prompt:** qa_prompt_v3.md
* **Judge Prompt:** judge_relevance_prompt_v1.md
* **RAG model:** gemini-3.1-flash-lite
* **JUDGE model:** gemini-3.1-flash-lite
* **Test:** judge_test_v1.jsonl
## Caso de prueba 1

**Pregunta de evaluación:**
What are the steps to launch an EC2 instance using the AWS Management Console?

**Respuesta del sistema RAG:**
To launch an EC2 instance using the AWS Management Console, follow these steps:

1.  **Access the Console:** Open the Amazon EC2 console at https://console.aws.amazon.com/ec2/.
2.  **Select Region:** In the navigation bar at the top, ensure the correct AWS Region is selected.
3.  **Initiate Launch:** From the EC2 console dashboard, choose **Launch instance**.
4.  **Name the Instance:** Under **Name and tags**, enter a descriptive name for your instance.
5.  **Select OS and AMI:** Under **Application and OS Images (Amazon Machine Image)**, choose an operating system (such as Amazon Linux) and select an AMI. You can choose **Quick Start** for common options or **Browse more AMIs** to search for others.
6.  **Choose Instance Type:** Under **Instance type**, select the hardware configuration (CPU, memory, etc.) that meets your needs. You can use the "Compare instance types" or "Get advice" features if you are unsure which to select.
7.  **Configure Key Pair:** Under **Key pair (login)**, select an existing key pair or create a new one. This is required to connect to your instance using standard methods.
8.  **Configure Network Settings:** Under **Network settings**, you can use the default VPC and subnet settings, or configure them as required. You can also configure security groups to control traffic to your instance.
9.  **Review and Launch:** Review your settings in the **Summary** panel and choose **Launch instance**.

**Notes:**
*   If you are launching an instance for production, you should configure all parameters to meet your specific requirements.
*   If you are testing, you can use the "Quickly launch" path, which uses default values for most parameters.
*   Once the instance is in the "running" state, you can select it in the console and choose **Connect** to access it.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer provides a clear, step-by-step guide that directly addresses the user's query. It incorporates all the expected concepts mentioned in the prompt (selecting an AMI, instance type, network settings, storage/security groups, and launching) and is well-structured, accurate to the provided context, and free of irrelevant information.

## Caso de prueba 2

**Pregunta de evaluación:**
What is the difference between On-Demand, Reserved, and Spot Instances in EC2?

**Respuesta del sistema RAG:**
In Amazon EC2, there are three primary purchasing options for compute capacity, each designed for different workload requirements and cost structures:

### **On-Demand Instances**
*   **Usage:** Best for short-term, irregular workloads that cannot be interrupted.
*   **Commitment:** No long-term commitment. You pay for compute capacity by the second (with a 60-second minimum) only while the instance is in the running state.
*   **Control:** You have full control over the instance lifecycle (launch, stop, hibernate, start, reboot, or terminate).
*   **Pricing:** Prices are fixed and static.

### **Reserved Instances (RI)**
*   **Usage:** Best for steady-state workloads. They are not physical instances, but rather a billing discount applied to the use of On-Demand Instances in your account.
*   **Commitment:** Requires a one-year or three-year term commitment. You pay for the entire term regardless of actual use.
*   **Flexibility:** You can choose between "Regional" RIs (which provide a discount) or "Zonal" RIs (which provide both a discount and a capacity reservation in a specific Availability Zone).
*   **Pricing:** Provides significant savings compared to On-Demand pricing. Payment options include All Upfront, Partial Upfront, or No Upfront.
*   **Note:** AWS recommends Savings Plans over Reserved Instances for greater flexibility.

### **Spot Instances**
*   **Usage:** Best for fault-tolerant, flexible, and stateless workloads (e.g., big data, containerized workloads, CI/CD, or batch jobs) where you can be flexible about when applications run.
*   **Commitment:** None.
*   **Interruption:** These instances use spare EC2 capacity and can be interrupted by Amazon EC2 with a two-minute notice if the capacity is needed back.
*   **Pricing:** Offers the deepest discounts (up to 90% compared to On-Demand). The hourly "Spot price" is set by Amazon EC2 and fluctuates based on long-term supply and demand.

### **Summary Comparison**
| Feature | On-Demand | Reserved Instances | Spot Instances |
| :--- | :--- | :--- | :--- |
| **Commitment** | None | 1 or 3 years | None |
| **Pricing** | Fixed/Static | Discounted | Variable (Supply/Demand) |
| **Interruption** | You control | N/A | Can be interrupted by AWS |
| **Best For** | Unpredictable workloads | Steady-state workloads | Flexible, fault-tolerant tasks |

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer directly and accurately addresses the user's query by defining the three EC2 instance types (On-Demand, Reserved, and Spot) and explaining their differences in terms of usage, commitment, and pricing. It incorporates all the expected concepts and provides a clear, structured summary that is easy to understand.

## Caso de prueba 3

**Pregunta de evaluación:**
How does EC2 handle idempotency in API requests?

**Respuesta del sistema RAG:**
In Amazon EC2, idempotency ensures that an API request completes no more than one time. This is critical for handling scenarios where a request might time out or encounter server issues before completion, preventing the unintended creation of multiple resources.

### How Idempotency Works
*   **Idempotent by Default:** Certain API actions are idempotent by default and do not require additional configuration. Examples include `AssociateAddress`, `CreateVpnConnection`, `DisassociateAddress`, `ReplaceNetworkAclAssociation`, and `TerminateInstances`.
*   **Client Token Idempotency:** For other API actions, you can achieve idempotency by providing a `ClientToken` in your request. A client token is a unique, case-sensitive string of up to 64 ASCII characters.
    *   If you retry a request with the same client token and the same parameters, the operation succeeds without performing any additional actions.
    *   If you retry with the same token but different parameters (excluding Region or Availability Zone), the request will fail with an `IdempotentParameterMismatch` error.
    *   You should not reuse the same client token for different API requests.

### Types of Idempotency for `RunInstances`
The `RunInstances` action supports both Regional and Zonal idempotency, depending on how you specify the Availability Zone:

1.  **Regional Idempotency:** Used if you do not explicitly or implicitly specify an Availability Zone. The request is idempotent within a specific Region. You can use the same client token to launch instances in a different Region, but it will only complete once within the original Region.
2.  **Zonal Idempotency:** Used if you explicitly specify an Availability Zone (via the `Placement` data type) or implicitly specify one (via a `SubnetId`). The request is idempotent within that specific Availability Zone. You can use the same client token to launch instances in different Availability Zones within the same Region.

### Implementation
*   **API Requests:** Include the `ClientToken` parameter in your request.
*   **AWS CLI:** Add the `--client-token` option to your command.

### Retry Recommendations
*   **200 (OK):** Do not retry. The request completed successfully.
*   **400-series (Client Errors):** Do not retry. These indicate issues such as invalid parameters or insufficient permissions.
*   **General Advice:** Because an API request might return a result before asynchronous workflows are finished, it is recommended to confirm the state of your resources (e.g., using `DescribeInstances`) if you are unsure of the outcome.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer is excellent. It directly addresses the user's query by explaining the concept of idempotency in EC2, the role of the client token, the distinction between default and optional idempotency, the specific types of idempotency (Regional vs. Zonal) for RunInstances, and provides practical implementation and retry guidance. It is complete, accurate based on the provided context, and free of irrelevant information.

## Caso de prueba 4

**Pregunta de evaluación:**
What is an Amazon Machine Image (AMI) and what are its key characteristics?

**Respuesta del sistema RAG:**
An Amazon Machine Image (AMI) is a template that provides the software configuration—including the operating system, applications, and services—required to set up and boot an Amazon EC2 instance. When you launch an instance, you must specify an AMI.

An AMI also contains a block device mapping that specifies the block devices to attach to the instance upon launch. You can use AMIs provided by AWS, public AMIs, AMIs shared with you, or AMIs purchased through the AWS Marketplace. You can also create your own custom AMIs by launching an instance, customizing it, and saving that configuration as a new image.

**Key Characteristics of an AMI:**
An AMI is specific to the following attributes, which you should consider to ensure compatibility with your chosen instance type:

*   **Region:** AMIs are specific to the AWS Region in which they are located. If you need to use an AMI in a different Region, you must copy it there.
*   **Operating System:** The OS (e.g., Linux, Windows) contained within the image.
*   **Processor Architecture:** The architecture required for the instance.
*   **Root Volume Type:** AMIs are categorized by their root device type, which is either backed by Amazon EBS or backed by instance store.
*   **Virtualization Type:** The virtualization method (e.g., HVM or paravirtual) required by the instance type.
*   **Launch Permissions:** These determine who can use the AMI to launch instances. Permissions can be private (owned by you or shared with specific accounts/organizations) or public (available to all AWS accounts).

Additionally, when selecting an AMI, you may need to consider other factors such as the **boot mode** (e.g., legacy-bios, uefi) and any **additional software** pre-installed on the image.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer provides a clear and accurate definition of an AMI as a template for EC2 instances. It explicitly lists all the key characteristics requested (launch permissions, root volume type, and virtualization type) along with other relevant attributes mentioned in the provided context. The information is well-structured, directly responsive, and free of irrelevant content.

## Caso de prueba 5

**Pregunta de evaluación:**
How do security groups work in Amazon EC2?

**Respuesta del sistema RAG:**
Security groups in Amazon EC2 act as a virtual firewall for your instances, controlling both inbound and outbound network traffic at the instance level. Here is how they function:

*   **Traffic Control:** You add rules to a security group to allow specific traffic to or from associated instances. Inbound rules govern incoming traffic, while outbound rules govern outgoing traffic.
*   **Stateful Nature:** Security groups are stateful. If you send a request from your instance, the response traffic for that request is automatically allowed to flow back in, regardless of inbound rules. Similarly, responses to allowed inbound traffic are permitted to flow out, regardless of outbound rules.
*   **Association:** You can associate multiple security groups with a single instance, and each security group can be associated with multiple instances. When multiple security groups are associated with an instance, Amazon EC2 effectively aggregates all the rules to create one set of permissions.
*   **Default Behavior:** When you launch an instance without specifying a security group, Amazon EC2 uses the default security group for the VPC. New security groups start with an outbound rule that allows all traffic to leave the resource, but they do not allow any inbound traffic by default.
*   **Evaluation:** When Amazon EC2 determines whether to allow traffic to reach an instance, it evaluates all rules from all security groups associated with that instance. If there is more than one rule for a specific port, Amazon EC2 applies the most permissive rule.
*   **Shared Responsibility:** Security is a shared responsibility between you and AWS. While AWS provides security groups as a tool, you are responsible for configuring them to meet your specific security requirements. If your needs are not fully met by security groups, you can maintain your own firewall on your instances in addition to using them.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer is excellent. It directly addresses the query by explaining how security groups work, covering all the core concepts requested (virtual firewall, inbound/outbound control, rules) and including important additional details like their stateful nature, aggregation of rules, and default behaviors, all of which are supported by the provided context.

## Caso de prueba 6

**Pregunta de evaluación:**
What is EC2 API request throttling and how should developers handle it?

**Respuesta del sistema RAG:**
Amazon EC2 implements API request throttling to maintain service performance and ensure fair usage for all customers. Throttling occurs when API requests exceed the maximum allowed limits for your AWS account on a per-Region basis. This applies to requests originating from the AWS console, command-line tools, and third-party applications.

### How Throttling Works
EC2 uses a **token bucket algorithm** to manage these limits:
*   **Token Buckets:** Each account has a bucket for API actions that holds a specific number of tokens. Each request consumes a token.
*   **Bucket Refill:** Buckets refill at a set rate. If you deplete your tokens, you can continue to make requests at the refill rate.
*   **Types of Throttling:**
    *   **Request Rate Limiting:** Evaluates each API individually (e.g., `DescribeHosts`).
    *   **Resource Rate Limiting:** Applies to specific actions like `RunInstances` or `TerminateInstances`. These actions have a separate bucket that depletes based on the number of resources impacted, in addition to the standard request rate limit.

If you exceed these limits, you will receive a `RequestLimitExceeded` error code.

### How Developers Should Handle Throttling
To handle throttling gracefully, developers should implement the following strategies:

1.  **Implement Exponential Backoff:** When you receive a throttling error or a 5xx server error, use an exponential backoff algorithm to calculate the sleep interval between retries. This involves using progressively longer waits between consecutive retries.
2.  **Use Jitter:** Incorporate randomized delays (jitter) into your retry logic to prevent successive collisions.
3.  **Leverage AWS SDKs:** Each AWS SDK includes built-in automatic retry logic, which should be utilized.
4.  **Monitor Usage:** Use Amazon CloudWatch to track API throttling metrics and set up alarms to warn you when you are approaching your limits.
5.  **Optimize Requests:**
    *   Use pagination and filtering for "Describe" actions to ensure you are using the larger, standard token buckets rather than the smaller buckets reserved for unfiltered/unpaginated requests.
    *   For resource status updates, avoid aggressive polling. Give the request time to complete, and use an increasing or variable sleep interval if you must poll. Alternatively, use Amazon EventBridge to receive notifications of state changes.
6.  **Request a Limit Increase:** If your application consistently hits these limits, you can request an increase via the AWS Support Center. When doing so, prioritize increasing the bucket refill rate before the maximum capacity, and ensure you specify which API actions require the increase.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer is excellent. It directly addresses the query by explaining what EC2 API throttling is (using the token bucket algorithm and the two types of rate limiting) and provides a comprehensive list of strategies for developers to handle it (exponential backoff, jitter, SDK usage, monitoring, optimization, and requesting limit increases). It is well-structured, accurate based on the provided context, and contains no irrelevant information.

## Caso de prueba 7

**Pregunta de evaluación:**
How can I connect to my EC2 instance after launching it?

**Respuesta del sistema RAG:**
To connect to your EC2 instance after it has been launched, you must first ensure the instance is in the **running** state and has passed all status checks. You can verify this by selecting your instance in the Amazon EC2 console and checking the **Instance state** and **Status check** columns.

The method you use to connect depends on your local computer's operating system and the configuration of your instance. Here are the primary ways to connect:

### 1. Connecting via SSH Client
This is a standard method for Linux instances.
1. **Check for an SSH client:** Open a terminal on your local computer and type `ssh`. If the command is recognized, you are ready. If not, you must install an SSH client (such as OpenSSH for Windows).
2. **Locate connection details:** In the Amazon EC2 console, select your instance and choose **Connect**. Navigate to the **SSH client** tab.
3. **Set permissions (if applicable):** If you are using a private key file (`.pem`) on Linux or macOS, you may need to run a `chmod` command to set the correct permissions for your key file.
4. **Run the SSH command:** Copy the example SSH command provided in the console. It will look similar to:
   `ssh -i key-pair-name.pem ec2-user@public-dns-name`
5. **Execute:** Run this command in your terminal. If the key file is not in your current directory, provide the full path to the file.

### 2. Connecting via EC2 Instance Connect
This method allows you to connect through the browser-based console.
* **Prerequisites:** The instance must have a public IPv4 or IPv6 address (unless using an EC2 Instance Connect Endpoint) and must have the EC2 Instance Connect package installed.
* **Procedure:** In the Amazon EC2 console, select your instance and choose **Connect**. Follow the prompts to connect directly through the browser.

### Important Considerations
* **Security Groups:** Ensure your security group has an inbound rule that allows SSH traffic from your specific IP address. If the connection times out, verify that your security group rules are configured correctly.
* **Key Pairs:** If you launched your instance without a key pair, you will not be able to connect using the standard SSH method described above.
* **Username:** Be aware that you may need to use a specific username (such as `ec2-user` for Amazon Linux) depending on the AMI you used to launch the instance.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer is excellent. It directly addresses the user's query by outlining the necessary steps to connect to an EC2 instance. It covers the core concepts requested (SSH, key pairs, public DNS/IP, and instance state verification) and provides a clear, structured guide. It also includes important prerequisites like security group configuration and instance status, making it a complete and helpful response.

## Caso de prueba 8

**Pregunta de evaluación:**
What are EC2 placement groups and when should I use each strategy?

**Respuesta del sistema RAG:**
EC2 placement groups are an optional feature that allows you to influence the placement of a group of interdependent instances to meet the needs of your workload. You can create a maximum of 500 placement groups per Region, and an instance can belong to only one placement group at a time.

There are three placement strategies available, each designed for specific use cases:

### 1. Cluster Placement Groups
*   **What it is:** A logical grouping of instances within a single Availability Zone. Instances are placed in the same high-bisection bandwidth segment of the network.
*   **When to use it:** Recommended for applications that benefit from low network latency, high network throughput, or both. It is ideal for tightly-coupled node-to-node communication, such as high-performance computing (HPC) applications, where the majority of network traffic occurs between instances in the group.

### 2. Partition Placement Groups
*   **What it is:** A strategy that divides the placement group into logical segments called "partitions." EC2 ensures that each partition has its own set of racks, with its own network and power source.
*   **When to use it:** Recommended for large distributed and replicated workloads, such as HDFS, HBase, Cassandra, and Kafka. This strategy helps isolate the impact of hardware failure within your application by ensuring that groups of instances in one partition do not share underlying hardware with those in other partitions.

### 3. Spread Placement Groups
*   **What it is:** A group of instances that are each placed on distinct underlying hardware.
*   **When to use it:** Recommended for applications that have a small number of critical instances that should be kept separate from each other to reduce the risk of simultaneous failures caused by shared equipment. 
    *   **Rack level:** Available in AWS Regions and on AWS Outposts.
    *   **Host level:** Available only with AWS Outposts.

**Key Considerations:**
*   **Pricing:** There is no charge for creating a placement group.
*   **Capacity:** If you launch instances into a placement group and there is insufficient unique hardware to fulfill the request, the launch will fail.
*   **Flexibility:** If you do not use a placement group, EC2 automatically attempts to spread your instances across underlying hardware to minimize correlated failures.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer directly and accurately addresses the user's query by defining EC2 placement groups and explaining the three specific strategies (Cluster, Partition, and Spread) along with their recommended use cases. It is well-structured, uses the provided context effectively, and includes no irrelevant information.

## Caso de prueba 9

**Pregunta de evaluación:**
How do I use the AWS SDK or CLI to programmatically manage EC2 resources?

**Respuesta del sistema RAG:**
You can programmatically manage Amazon EC2 resources using several interfaces, including the AWS Command Line Interface (AWS CLI), AWS SDKs, and AWS Tools for PowerShell.

### Using the AWS Command Line Interface (AWS CLI)
The AWS CLI allows you to interact with EC2 services directly from your command-line shell. It is supported on Windows, Mac, and Linux.
*   **Access:** You can use it to perform various operations, such as managing instances, security groups, and network configurations.
*   **Reference:** For specific syntax and command examples, refer to the **AWS CLI Command Reference** for EC2.
*   **Example:** To collect logs for EC2Launch v2, you would use a command like:
    `ec2launch collect-logs -o C:\Mylogs.zip`

### Using AWS SDKs
AWS provides SDKs for various programming languages, which allow you to build applications that manage EC2 resources using language-specific APIs. These SDKs handle tasks such as cryptographically signing requests, retrying requests, and managing error responses.
*   **Components:** SDKs provide pre-built libraries, compilers, and debuggers to make development more efficient.
*   **Implementation:** You can use SDKs to implement "Basics" (essential operations), "Actions" (individual service functions), or "Scenarios" (complex tasks involving multiple functions or services).
*   **Examples:** AWS provides code examples for common tasks, such as starting instances or managing Auto Scaling groups, which can be found in the AWS Code Examples Repository on GitHub.

### Using AWS Tools for PowerShell
These modules are built on the functionality of the SDK for .NET and allow you to script operations on your AWS resources directly from the PowerShell command line. You can find the specific cmdlets for Amazon EC2 in the **AWS Tools for PowerShell Cmdlet Reference**.

### Additional Resources
*   **CloudFormation:** You can also manage resources by creating JSON or YAML templates that describe your infrastructure, allowing you to provision and configure resources consistently across different regions and accounts.
*   **Code Examples:** For a complete list of developer guides and code examples, you can refer to the "Create Amazon EC2 resources using an AWS SDK" section in the AWS documentation.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer directly addresses the user's query by explaining how to use both the AWS CLI and AWS SDKs to manage EC2 resources. It covers the core concepts requested, including the role of the CLI, the benefits of using SDKs (such as handling retries and signing), and provides context on where to find code examples and documentation. The answer is well-structured, relevant, and complete based on the provided context.

## Caso de prueba 10

**Pregunta de evaluación:**
What is the role of Elastic IP addresses in EC2 and how are they used?

**Respuesta del sistema RAG:**
An Elastic IP address is a static, public IPv4 address designed for dynamic cloud computing. Its primary role is to provide a fixed, predictable IP address that remains constant even if your EC2 instance is stopped, restarted, or replaced.

### Key Characteristics
*   **Static Nature:** Unlike standard public IPv4 addresses that may change when an instance is stopped and started, an Elastic IP address remains associated with your account until you explicitly release it.
*   **Regional Scope:** Elastic IP addresses are specific to a single AWS Region and cannot be moved between Regions.
*   **Network Border Groups:** You must allocate an Elastic IP address in the same network border group as the resource you intend to associate it with.
*   **Cost:** You are charged for all Elastic IP addresses in your account, regardless of whether they are currently associated with a running instance or are idle.
*   **Quota:** By default, AWS accounts have a quota of five Elastic IP addresses per Region. You can request a quota increase through the Service Quotas console if your architecture requires more.

### How They Are Used
Elastic IP addresses are primarily used to maintain consistent connectivity to your applications. They are particularly useful for remapping addresses to a different instance in the event of an instance failure.

**The typical lifecycle involves these steps:**
1.  **Allocation:** You first allocate an Elastic IP address to your AWS account from Amazon's pool (or your own custom pool).
2.  **Association:** You associate the allocated address with a specific resource, such as an EC2 instance, a NAT gateway, or a Network Load Balancer. 
    *   *Note:* If the instance already has a public IPv4 address, that address is released back to the pool when the Elastic IP is associated.
3.  **Disassociation and Reassociation:** You can disassociate an Elastic IP from one resource and associate it with another at any time. 
4.  **Release:** If you no longer need the address, you must explicitly release it to stop incurring charges.

**Important Considerations:**
*   **DNS:** When you associate an Elastic IP with an instance, the instance's public DNS hostname changes to match the Elastic IP.
*   **Best Practices:** AWS recommends using Elastic IP addresses primarily for their ability to remap to new instances during failures and using DNS hostnames for other types of inter-node communication.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer is comprehensive, accurate, and directly addresses the user's query. It clearly defines the role of Elastic IP addresses (providing a static, fixed IP) and explains how they are used (allocation, association, remapping, and release). It also incorporates relevant details from the provided context, such as pricing, quotas, and best practices, without including unnecessary tangents.

## Caso de prueba 11

**Pregunta de evaluación:**
How do IAM roles work with EC2 instances for secure access to AWS services?

**Respuesta del sistema RAG:**
IAM roles provide a secure way for applications running on EC2 instances to access AWS services without the need to manually manage or distribute long-term security credentials (such as access keys and secret keys).

Here is how they work:

### 1. Delegation of Permissions
Instead of distributing credentials to each instance, you delegate permissions to the instance using an IAM role:
*   **Create the Role:** You define an IAM role and specify which AWS services or accounts can assume it.
*   **Define Access:** You attach policies to the role that define exactly which API actions and resources the application is permitted to use.
*   **Attach to Instance:** You associate the role with your EC2 instance. This is done via an **instance profile**, which acts as a container for the IAM role.

### 2. Secure Credential Retrieval
Once a role is attached, applications running on the instance do not need to handle credentials directly. Instead:
*   **Automatic Retrieval:** AWS SDKs, the AWS CLI, and Tools for Windows PowerShell automatically retrieve temporary security credentials from the **Instance Metadata Service (IMDS)**.
*   **Temporary Credentials:** The credentials provided are temporary and are automatically rotated by AWS, eliminating the security risks associated with hardcoding or manually updating credentials on instances.

### 3. Best Practices
*   **Least Privilege:** Always associate the role with policies that grant only the minimum permissions required for the application to function. You can use IAM Access Analyzer to generate policies based on actual access activity to ensure you are adhering to this principle.
*   **Instance Profiles:** While you can only attach one IAM role to an instance, you can attach the same role to many instances. If you create a role via the IAM console, an instance profile with the same name is created automatically. If you use the CLI or API, you must create the role and the instance profile as separate actions.
*   **Security:** Ensure that you do not expose your credentials when services (such as HTTP proxies or XML processors) make HTTP calls on your behalf, as these services might inadvertently access the instance metadata.

### 4. Instance Identity Roles
In addition to the roles you assign, every EC2 instance has an **instance identity role** automatically created at launch. This role is used by specific AWS services (such as Amazon GuardDuty, AWS Systems Manager, and EC2 Instance Connect) to identify the instance and perform service-specific tasks. These credentials are also accessible via the IMDS but are distinct from the IAM role you attach to the instance for your own applications.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer directly and comprehensively addresses the user's query. It explains the mechanism of IAM roles on EC2 (delegation, instance profiles, and IMDS), highlights the security benefits (avoiding hardcoded credentials, temporary/rotated credentials), and incorporates the principle of least privilege as requested. It also provides additional relevant context from the retrieved documents, such as the distinction between user-assigned roles and instance identity roles.

## Caso de prueba 12

**Pregunta de evaluación:**
What are the best practices for securing an EC2 instance?

**Respuesta del sistema RAG:**
To secure your Amazon EC2 instances, you should implement a defense-in-depth strategy that covers identity management, network security, storage, and ongoing maintenance. Based on the provided documentation, here are the recommended best practices:

### Identity and Access Management
*   **Use IAM Roles:** Manage access to AWS resources and APIs using IAM roles and identity federation rather than long-term credentials.
*   **Principle of Least Privilege:** Grant users and applications only the minimum set of permissions necessary to perform their functions.
*   **Secure Account Credentials:** Protect your AWS account credentials, use Multi-Factor Authentication (MFA), and set up individual users via IAM or AWS IAM Identity Center.

### Network Security
*   **Security Groups:** Implement the least permissive rules possible. Use security groups as your primary mechanism for stateful packet filtering, allowing only necessary traffic from known IP addresses or specific protocols (e.g., HTTPS).
*   **Network ACLs:** Use network ACLs sparingly as a secondary, stateless control to provide subnet-level guard rails.
*   **Traffic Monitoring:** Use VPC Flow Logs to monitor traffic, and utilize tools like Reachability Analyzer or Network Access Analyzer to identify unintended network accessibility.
*   **Windows-Specific Controls:** For Windows instances, use Windows Firewall to layer security and manage settings centrally via Group Policy Objects (GPO).

### Storage Security
*   **Encryption:** Always encrypt EBS volumes and snapshots.
*   **Data Separation:** Use separate EBS volumes for the operating system and your data to ensure data persistence after instance termination.
*   **Instance Store:** Use instance store only for temporary data, as it is deleted when an instance is stopped, hibernated, or terminated.

### Maintenance and Monitoring
*   **Patching and Updates:** Regularly patch and update the operating system and applications. You can automate this process using AWS Systems Manager Patch Manager.
*   **Vulnerability Scanning:** Use Amazon Inspector to automatically discover and scan instances for software vulnerabilities and unintended network exposure.
*   **Threat Detection:** Use Amazon GuardDuty (including Malware Protection and Runtime Monitoring) to identify suspicious behavior and potential threats.
*   **Compliance Monitoring:** Use AWS Security Hub CSPM controls to monitor your resources against security best practices and standards.
*   **Security Baselines:** Adhere to organizational security standards. For Windows, consider benchmarks from Microsoft, CIS, or NIST, and install software to protect against malicious code and monitor host integrity.

### Data Protection
*   **Communication:** Use SSL/TLS (TLS 1.2 or 1.3) for all communications with AWS resources.
*   **Logging:** Enable API and user activity logging using AWS CloudTrail.
*   **FIPS Compliance:** If required, use FIPS endpoints when accessing AWS through the CLI or API.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer is comprehensive, well-structured, and directly addresses the user's query by synthesizing the provided documentation. It covers all the core aspects requested (IAM, network security, patching, monitoring) and includes additional relevant best practices found in the context (storage, data protection, threat detection). It is accurate to the provided text and free of irrelevant tangents.

## Caso de prueba 13

**Pregunta de evaluación:**
How does EBS (Elastic Block Store) integrate with EC2 and what are its volume types?

**Respuesta del sistema RAG:**
Amazon Elastic Block Store (Amazon EBS) integrates with Amazon EC2 by providing durable, block-level storage volumes that can be attached to and detached from your instances. 

### Integration with EC2
*   **Persistence:** EBS volumes persist independently of the life of the associated EC2 instance. This means data remains available even if the instance is stopped or terminated (provided the volume is not set to be deleted upon termination).
*   **Flexibility:** You can attach multiple EBS volumes to a single instance. They function similarly to local drives, allowing the instance to interact with them as block storage.
*   **Management:** You can attach volumes during instance launch or at any time after the instance is running. Additionally, you can increase the size or performance of EBS volumes without needing to detach them or restart the instance.
*   **Data Protection:** You can encrypt EBS volumes and create snapshots—which are stored in Amazon S3—to serve as backup copies. These snapshots can be used to restore volumes or migrate data across AWS Regions, Availability Zones, or accounts.
*   **Performance:** For optimal performance, you can use EBS-optimized instances. Some instance types support multiple "EBS cards," which allow for higher throughput and IOPS by spreading the instance's maximum performance across those cards.

### Volume Types and Performance
While the provided documentation notes that specific volume types (such as `gp2`, `gp3`, `st1`, `sc1`, `io1`, `io2`, and `standard`) exist, it does not provide a detailed breakdown of the characteristics for every type. However, it does specify the following regarding performance configuration:
*   **Provisioning:** For `io1`, `io2`, and `gp3` volume types, you can specify the number of I/O operations per second (IOPS) the volume can support.
*   **Compatibility:** IOPS configuration is not supported for `gp2`, `st1`, `sc1`, or `standard` volumes.
*   **Best Practices:** For consistent bandwidth, it is recommended to match the provisioned IOPS of your volumes with the bandwidth available for your specific instance type.

**Evaluación del juez:**
- **score**: 4
- **reasoning**: The answer accurately describes how EBS integrates with EC2, covering persistence, attachment, management, and data protection. Regarding the volume types, the answer correctly identifies that the provided context mentions the existence of various types (gp2, gp3, st1, sc1, io1, io2, standard) but correctly notes that the provided text does not contain a detailed breakdown of their specific characteristics. It is a high-quality response based on the provided context, though it misses the 'expected' list of volume types as defined in the prompt's 'expected correct concepts' because that information was not present in the retrieved context.

## Caso de prueba 14

**Pregunta de evaluación:**
What is eventual consistency in EC2 and how can it affect API operations?

**Respuesta del sistema RAG:**
Eventual consistency in Amazon EC2 means that when you perform an operation to create or modify a resource, the change is not immediately visible to all other system components. Because it takes time for the resource's state or ID to propagate throughout the system, subsequent commands may fail if they are executed immediately after the initial request.

### How it affects API operations
Eventual consistency can cause API operations to return errors indicating that a resource does not exist, even if the initial creation command was successful. Common examples include:

*   **InvalidInstanceID.NotFound:** This may occur if you run a command using an instance ID immediately after a `RunInstances` call. It does not mean the instance failed to launch; rather, the system has not yet propagated the ID.
*   **InvalidGroup.NotFound:** Similar to instances, this can occur if you attempt to use a security group ID immediately after calling `CreateSecurityGroup`.

### How to manage eventual consistency
To handle these scenarios and ensure your operations succeed, you should implement the following strategies:

1.  **Use Exponential Backoff:** When you receive an error indicating a resource is not found, do not assume the operation failed. Instead, run the appropriate `Describe` command (e.g., `DescribeInstances` or `DescribeSecurityGroups`) repeatedly using an exponential backoff algorithm. Start with a wait time of a few seconds and gradually increase it up to a few minutes to allow the system time to propagate the resource information.
2.  **Confirm State Before Modification:** Before running a command to modify a resource, always confirm its current state by running the relevant `Describe` command.
3.  **Add Wait Time:** Even if a `Describe` command returns a successful response, it is recommended to add wait time between subsequent commands using an exponential backoff algorithm to ensure the system is fully synchronized.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately defines eventual consistency in the context of EC2, explains how it impacts API operations (specifically citing the 'not found' errors), and provides the recommended strategies for handling it (exponential backoff and confirming state) as outlined in the provided context.

## Caso de prueba 15

**Pregunta de evaluación:**
How can I monitor EC2 API usage and set up CloudWatch alarms for throttling events?

**Respuesta del sistema RAG:**
To monitor Amazon EC2 API requests and manage throttling, you can use Amazon CloudWatch. Below are the steps and considerations for setting this up:

### 1. Enable EC2 API Metrics
Amazon EC2 API metrics are an opt-in feature. You must request access to this feature before you can monitor these requests:
1. Open the **AWS Support Center**.
2. Choose **Create case** to request access to the EC2 API metrics feature for your account.

### 2. Monitor API Usage and Throttling
Once enabled, CloudWatch collects raw data on your API operations. You can use this to:
*   Track the usage and outcomes of API operations over time.
*   Identify and diagnose performance issues.
*   Monitor metrics specifically related to API throttling.

### 3. Create CloudWatch Alarms for Throttling
You can create CloudWatch alarms to warn you when you are approaching your API throttling limits. 

**General Procedure for Creating an Alarm:**
1. Open the **CloudWatch console**.
2. In the navigation pane, choose **Alarms**, then **All alarms**.
3. Choose **Create alarm**.
4. Choose **Select metric** and navigate to the **EC2/API** category.
5. Select the relevant metrics (such as those related to throttling or specific API actions like `DescribeInstances`).
6. Define the conditions for the alarm (e.g., setting a threshold for the number of errors or throttling events over a specific period).
7. Configure the alarm to send a notification (via Amazon SNS) or perform a specific action when the threshold is met.

**Important Considerations:**
*   **Permissions:** You must have `iam:CreateServiceLinkedRole` permissions to create or modify alarms that perform EC2 alarm actions.
*   **State Changes:** Alarms invoke actions for sustained state changes. The metric must maintain the threshold for the specified number of periods before an action is triggered.
*   **Retries:** If you encounter throttling errors (or server-side 5xx errors), your application should implement retries with exponential backoff. For client-side 4xx errors, you must correct the request before retrying.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer directly addresses the user's query by outlining the necessary steps to enable EC2 API metrics, explaining how to monitor them, and providing a clear procedure for setting up CloudWatch alarms for throttling. It incorporates the key concepts from the provided context, such as the opt-in requirement, the use of the CloudWatch console, and the importance of handling throttling via retries and exponential backoff.

## Resultado final: 4.933333333333334/5