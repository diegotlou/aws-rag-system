# Evaluación del sistema RAG para la prueba Faithfulness

* **System Prompt:** system_prompt_v3.md
* **QA Prompt:** qa_prompt_v3.md
* **Judge Prompt:** judge_faithfulness_prompt_v1.md
* **RAG model:** gemini-3.1-flash-lite
* **JUDGE model:** gemini-3.1-flash-lite
* **Test:** judge_test_v1.jsonl
## Caso de prueba 1

**Pregunta de evaluación:**
What are the steps to launch an EC2 instance using the AWS Management Console?

**Respuesta del sistema RAG:**
To launch an EC2 instance using the AWS Management Console, follow these steps:

1.  **Access the Console:** Open the Amazon EC2 console at https://console.aws.amazon.com/ec2/.
2.  **Select Region:** In the navigation bar at the top of the screen, ensure the correct AWS Region is selected.
3.  **Open the Wizard:** From the EC2 console dashboard, choose **Launch instance** to open the launch instance wizard.
4.  **Name the Instance:** Under **Name and tags**, enter a descriptive name for your instance.
5.  **Select an Image (AMI):** Under **Application and OS Images**, choose **Quick Start** and select your desired operating system (e.g., Amazon Linux). Ensure you select an AMI marked "Free Tier eligible" if you wish to utilize Free Tier benefits.
6.  **Choose Instance Type:** Under **Instance type**, select an instance type that meets your requirements. You can use the "Compare instance types" or "Get advice" features if you need assistance choosing. Ensure you select a "Free Tier eligible" type if applicable.
7.  **Configure Key Pair:** Under **Key pair (login)**, select an existing key pair or choose to create a new one. 
    *   *Warning:* Proceeding without a key pair is not recommended as it will prevent you from connecting to the instance using standard methods.
8.  **Configure Network Settings:** Under **Network settings**, you can typically keep the default VPC and subnet settings. You may also configure security groups to control traffic (e.g., allowing SSH, HTTP, or HTTPS).
9.  **Launch:** Review your settings in the **Summary** panel and choose **Launch instance**.

Once the instance is in the "running" state, you can select it in the console and choose **Connect** to access it. If the instance fails to launch or immediately terminates, refer to the troubleshooting documentation for EC2 instance launch issues.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The system answer accurately reflects the steps provided in the context chunks for launching an EC2 instance via the AWS Management Console. It correctly identifies the navigation to the console, region selection, the launch wizard, naming, AMI selection, instance type selection, key pair configuration, network/security group settings, and the final launch action. All claims are supported by the provided text.

## Caso de prueba 2

**Pregunta de evaluación:**
What is the difference between On-Demand, Reserved, and Spot Instances in EC2?

**Respuesta del sistema RAG:**
In Amazon EC2, there are three primary purchasing options for instances, each suited for different workload requirements and cost structures:

### **On-Demand Instances**
*   **Commitment:** No long-term commitment. You pay for compute capacity by the second with a 60-second minimum.
*   **Pricing:** Static, fixed hourly rates.
*   **Best For:** Applications with short-term, irregular workloads that cannot be interrupted.
*   **Control:** You have full control over the instance lifecycle (launch, stop, hibernate, start, reboot, or terminate).

### **Reserved Instances (RIs)**
*   **Commitment:** A one-year or three-year term commitment. You pay for the term regardless of actual usage.
*   **Pricing:** Provides significant savings compared to On-Demand pricing. You can pay All Upfront, Partial Upfront, or No Upfront.
*   **Nature:** These are not physical instances, but a billing discount applied to On-Demand Instances that match specific attributes (instance type, Region, platform, and tenancy).
*   **Scope:**
    *   **Regional:** Applies a discount to running On-Demand Instances.
    *   **Zonal:** Provides both a billing discount and a capacity reservation for a specific Availability Zone.
*   **Note:** AWS recommends Savings Plans over Reserved Instances for greater flexibility.

### **Spot Instances**
*   **Commitment:** None. These use spare EC2 capacity.
*   **Pricing:** The Spot price is set by Amazon EC2 and fluctuates based on long-term supply and demand. This can offer savings of up to 90% compared to On-Demand prices.
*   **Availability:** There is no guarantee that capacity will be available. If Amazon EC2 needs the capacity back, it will interrupt your instance with a two-minute warning.
*   **Best For:** Stateless, fault-tolerant, and flexible applications such as big data, containerized workloads, CI/CD, batch jobs, and high-performance computing. They are not suitable for stateful or fault-intolerant workloads.

### **Summary Comparison**
| Feature | On-Demand | Spot |
| :--- | :--- | :--- |
| **Pricing** | Static | Varies based on supply/demand |
| **Interruption** | You control the lifecycle | Can be interrupted by AWS (2-min notice) |
| **Capacity** | Guaranteed if available | Subject to availability |
| **Use Case** | Irregular, non-interruptible | Flexible, fault-tolerant |

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the information provided in the context chunks. Every claim regarding the commitment, pricing, and use cases for On-Demand, Reserved, and Spot instances is supported by the retrieved text. The summary table also correctly synthesizes the differences described in the provided documentation.

## Caso de prueba 3

**Pregunta de evaluación:**
How does EC2 handle idempotency in API requests?

**Respuesta del sistema RAG:**
In Amazon EC2, idempotency ensures that a mutating API request completes no more than one time. If an original request succeeds, any subsequent retries with the same parameters and client token will also succeed without performing any additional actions. This prevents the unintended creation of multiple resources when retrying requests that may have timed out or encountered server issues.

### How Idempotency Works
*   **Default Idempotency:** Certain API actions (such as `TerminateInstances`, `AssociateAddress`, and `CreateVpnConnection`) are idempotent by default and do not require extra configuration.
*   **Client Token Idempotency:** For other actions, you can achieve idempotency by providing a `ClientToken` in your request. This is a unique, case-sensitive string of up to 64 ASCII characters.
    *   **Successful Retries:** If you retry a request that already completed successfully using the same token and parameters, the retry succeeds without repeating the action.
    *   **Parameter Mismatch:** If you retry a request using the same token but with different parameters (other than Region or Availability Zone), the request will fail with an `IdempotentParameterMismatch` error.
    *   **Best Practice:** You should not reuse the same client token for different API requests.

### Types of Idempotency for `RunInstances`
The `RunInstances` action supports both Regional and Zonal idempotency, depending on how you specify the target:
*   **Regional Idempotency:** Used if you do not explicitly or implicitly specify an Availability Zone. The request is idempotent within a Region, but the same token can be used to launch instances in different Regions.
*   **Zonal Idempotency:** Used if you explicitly specify an Availability Zone (via the `Placement` data type) or implicitly specify one (via a `SubnetId`). The request is idempotent within that specific Availability Zone.

### Implementation
*   **API Requests:** Include the `ClientToken` parameter in your request.
*   **AWS CLI:** Add the `--client-token` option to your command.

### Retry Recommendations
*   **200 (OK):** Do not retry; the original request was successful.
*   **400-series (Client Errors):** Do not retry, as these indicate issues like invalid parameters or insufficient permissions.
*   **General Note:** Because an API request might return a result before asynchronous workflows are complete, it is recommended to confirm the state of your resources (e.g., using `DescribeInstances`) if you are unsure of the outcome.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the information provided in the context. It correctly identifies the definition of idempotency, the distinction between default and client-token-based idempotency, the specific behavior of the ClientToken (including the IdempotentParameterMismatch error), the types of idempotency for RunInstances (Regional vs. Zonal), and the retry recommendations. All claims are directly supported by the provided text.

## Caso de prueba 4

**Pregunta de evaluación:**
What is an Amazon Machine Image (AMI) and what are its key characteristics?

**Respuesta del sistema RAG:**
An Amazon Machine Image (AMI) is a template that provides the software configuration—including the operating system, applications, and services—required to set up and boot an Amazon EC2 instance. When you launch an instance, you must specify an AMI.

An AMI also contains a block device mapping that specifies the block devices to attach to the instance upon launch. You can use AMIs provided by AWS, public AMIs, AMIs shared with you, or AMIs purchased from the AWS Marketplace. Additionally, you can create your own custom AMIs by launching an instance, customizing it, and then saving that configuration as a new image.

**Key Characteristics of an AMI:**
An AMI is specific to the following attributes, which you must consider to ensure compatibility with your chosen instance type:

*   **Region:** AMIs are specific to the AWS Region in which they are located. If you need to use an AMI in a different Region, you must copy it there.
*   **Operating System:** The OS installed on the image (e.g., Linux or Windows).
*   **Processor Architecture:** The architecture required for the instance (e.g., x86_64).
*   **Root Volume Type:** AMIs are categorized by their root device type, which is either backed by Amazon EBS or backed by instance store.
*   **Virtualization Type:** The virtualization method required (e.g., HVM or paravirtual).
*   **Launch Permissions:** These determine who can use an AMI to launch instances. Permissions can be public (available to all AWS accounts), explicit (shared with specific accounts, organizations, or OUs), or implicit (owned by you).

Additionally, when selecting an AMI, you may need to consider other factors such as the **boot mode** (e.g., legacy-bios, uefi, or uefi-preferred) and whether the image is a "paid AMI" from the AWS Marketplace, which may involve additional usage fees.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately defines an AMI and its key characteristics based on the provided context. Every claim, including the definition, the role of block device mappings, the ability to create custom AMIs, and the specific characteristics (Region, OS, Processor architecture, Root volume type, Virtualization type, Launch permissions, and Boot mode), is directly supported by the retrieved text.

## Caso de prueba 5

**Pregunta de evaluación:**
How do security groups work in Amazon EC2?

**Respuesta del sistema RAG:**
Security groups in Amazon EC2 act as a virtual firewall for your instances, controlling both inbound and outbound network traffic at the instance level. Here is how they function:

*   **Traffic Control:** You define rules for each security group to allow specific traffic to or from associated instances. Inbound rules govern incoming traffic, while outbound rules govern outgoing traffic.
*   **Stateful Nature:** Security groups are stateful. This means that if you send a request from your instance, the response traffic for that request is automatically allowed to flow back in, regardless of inbound rules. Similarly, responses to allowed inbound traffic are permitted to flow out, regardless of outbound rules.
*   **Association:** You can associate multiple security groups with a single instance, and each security group can be associated with multiple instances. When multiple security groups are associated with an instance, the rules from all of them are aggregated to determine whether traffic is allowed.
*   **Default Behavior:** When you launch an instance without specifying a security group, Amazon EC2 uses the default security group for the VPC. New security groups start with an outbound rule that allows all traffic to leave the resource, but they contain no inbound rules by default.
*   **Evaluation:** When Amazon EC2 decides whether to allow traffic to reach an instance, it evaluates all rules from all security groups associated with that instance. If there is more than one rule for a specific port, Amazon EC2 applies the most permissive rule.
*   **Shared Responsibility:** Security groups are a tool provided by AWS for you to secure your instances. You are responsible for configuring them to meet your specific security needs. If your requirements are not fully met by security groups, you can maintain your own firewall on your instances in addition to using them.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the information provided in the context. Every claim made—regarding traffic control, stateful nature, association, default behavior, rule evaluation, and shared responsibility—is directly supported by the provided text.

## Caso de prueba 6

**Pregunta de evaluación:**
What is EC2 API request throttling and how should developers handle it?

**Respuesta del sistema RAG:**
Amazon EC2 implements API request throttling to maintain service performance and ensure fair usage across all customers. Throttling limits apply to requests originating from the Amazon EC2 console, command-line tools, and third-party applications.

### How Throttling Works
EC2 uses a **token bucket algorithm** to manage these limits. Your account has a "bucket" for each API that holds a specific number of tokens, representing your throttling limit at any given second.

*   **Request Rate Limiting:** Each API is evaluated individually. Making a request consumes a token. If the bucket is empty, the request fails with a `RequestLimitExceeded` error. Buckets refill at a set rate per second until they reach their maximum capacity.
*   **Resource Rate Limiting:** Certain actions (like `RunInstances` or `TerminateInstances`) have separate resource token buckets that track the number of resources impacted, in addition to the standard request rate limits.

### How Developers Should Handle Throttling
If you receive a `Client.RequestLimitExceeded` error, you should handle it gracefully using the following strategies:

1.  **Implement Exponential Backoff:** When an API request fails due to throttling or a 5xx server error, use an exponential backoff algorithm to calculate the sleep interval between retries. This involves using progressively longer waits between consecutive retries.
2.  **Use Jitter:** Incorporate randomized delays (jitter) into your retry logic to prevent successive collisions.
3.  **Leverage AWS SDKs:** Each AWS SDK includes built-in automatic retry logic, which is the recommended way to handle these scenarios.
4.  **Optimize Requests:**
    *   **Use Pagination:** For "describe" actions that return large datasets, use pagination to stay within limits.
    *   **Use Filtering:** For non-mutating actions, use filtering to ensure tokens are deducted from the larger, standard token bucket rather than the smaller, unpaginated bucket.
    *   **Avoid Excessive Polling:** When checking for resource status updates, wait a few minutes before starting to poll, and use an increasing or variable sleep interval between requests. Consider using **Amazon EventBridge** to receive notifications for state changes instead of manual polling.
5.  **Monitor Limits:** Use Amazon CloudWatch to track API throttling metrics and set up alarms to warn you when you are approaching your limits.
6.  **Request a Limit Increase:** If your application consistently hits these limits, you can request an increase via the AWS Support Center. When doing so, prioritize increasing the bucket refill rate before the maximum capacity, and ensure you specify which API actions require the increase.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the provided context. It correctly explains the token bucket algorithm, the distinction between request and resource rate limiting, and provides the recommended strategies for handling throttling (exponential backoff, jitter, SDK usage, pagination, filtering, EventBridge, monitoring, and requesting limit increases) as described in the documentation.

## Caso de prueba 7

**Pregunta de evaluación:**
How can I connect to my EC2 instance after launching it?

**Respuesta del sistema RAG:**
To connect to your EC2 instance after it has been launched and is in the "running" state, you can use several methods depending on your requirements and your local computer's operating system.

### Prerequisites
Before attempting to connect, ensure the following:
*   **Instance Status:** Your instance must be in the "running" state and have passed all status checks.
*   **Network Connectivity:** Depending on your chosen method, your instance may need a public IPv4 or IPv6 address, or you must have established private network connectivity (such as VPN or VPC peering) if connecting via a private IP.
*   **Security Groups:** Ensure your security group rules allow inbound SSH traffic from your IP address.

### Connection Methods

#### 1. Using the Amazon EC2 Console (EC2 Instance Connect)
This method allows you to connect via an in-browser terminal.
1.  Open the [Amazon EC2 console](https://console.aws.amazon.com/ec2/).
2.  In the navigation pane, choose **Instances**.
3.  Select your instance and choose **Connect**.
4.  Select the **EC2 Instance Connect** tab.
5.  Choose **Connect using a Public IP**.
6.  Verify the username and choose **Connect**.

#### 2. Using an SSH Client
If you are using Linux, macOS, or Windows, you can connect using an SSH client from your local terminal.
1.  Open the [Amazon EC2 console](https://console.aws.amazon.com/ec2/) and select your instance.
2.  Choose **Connect** and select the **SSH client** tab.
3.  If you have a private key file (.pem), ensure its permissions are set correctly (e.g., using `chmod 400` on Linux/macOS).
4.  Copy the provided SSH command, which follows this format:
    `ssh -i key-pair-name.pem username@public-dns-name`
5.  Run this command in your local terminal.

#### 3. Using the AWS CLI (EC2 Instance Connect)
You can use the `ec2-instance-connect` CLI to connect via your local SSH client. This method automatically attempts to connect using available IP addresses (Public IPv4, then Private IPv4, then IPv6) based on your network configuration.

### Troubleshooting
*   **Connection Timeouts:** Verify your security group rules allow inbound SSH traffic from your specific IP address.
*   **Instance State:** If the instance is not running or has terminated, check the console for status details.
*   **Missing SSH Client:** If the `ssh` command is not recognized on your computer, you must install an SSH client (such as OpenSSH for Windows) before proceeding.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the provided context. It covers the prerequisites (instance state, network connectivity, security groups), the three primary connection methods mentioned (EC2 Instance Connect via console, SSH client, and AWS CLI), and includes relevant troubleshooting steps. All claims are directly supported by the provided text.

## Caso de prueba 8

**Pregunta de evaluación:**
What are EC2 placement groups and when should I use each strategy?

**Respuesta del sistema RAG:**
EC2 placement groups are an optional feature that allows you to influence the placement of a group of interdependent instances on underlying hardware to meet the needs of your workload. You can create a maximum of 500 placement groups per Region, and an instance can belong to only one placement group at a time.

There are three placement strategies available, each designed for specific use cases:

### 1. Cluster Placement Groups
*   **How it works:** Packs instances close together within a single Availability Zone. Instances are placed in the same high-bisection bandwidth segment of the network.
*   **When to use:** Recommended for applications that benefit from low network latency, high network throughput, or both. It is ideal for tightly coupled node-to-node communication, such as high-performance computing (HPC) applications.
*   **Key Considerations:** It cannot span multiple Availability Zones. It is recommended to use the same instance type for all instances in the group to ensure capacity availability.

### 2. Partition Placement Groups
*   **How it works:** Spreads instances across logical segments called "partitions." Each partition has its own set of racks, with its own network and power source, ensuring that groups of instances in one partition do not share hardware with those in another.
*   **When to use:** Designed for large distributed and replicated workloads, such as HDFS, HBase, Cassandra, and Kafka. It provides visibility into partition placement, allowing topology-aware applications to make intelligent data replication decisions.
*   **Key Considerations:** You can have a maximum of seven partitions per Availability Zone. It helps isolate the impact of hardware failure within your application.

### 3. Spread Placement Groups
*   **How it works:** Strictly places a small group of instances on distinct underlying hardware (racks or hosts).
*   **When to use:** Recommended for applications that have a small number of critical instances that must be kept separate from each other to reduce the risk of simultaneous failures caused by shared equipment.
*   **Key Considerations:** In a Region, a rack-level spread placement group is limited to a maximum of seven running instances per Availability Zone. If you need more than seven instances, you should use multiple spread placement groups.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the information provided in the context. It correctly defines EC2 placement groups, lists the three strategies (Cluster, Partition, Spread), explains how they work, and provides the recommended use cases and key considerations for each, all of which are supported by the provided text.

## Caso de prueba 9

**Pregunta de evaluación:**
How do I use the AWS SDK or CLI to programmatically manage EC2 resources?

**Respuesta del sistema RAG:**
You can programmatically manage Amazon EC2 resources using the AWS Command Line Interface (CLI), AWS SDKs, or the AWS Tools for PowerShell.

### Using the AWS CLI
The AWS CLI provides direct access to EC2 APIs from your command-line shell. It is supported on Windows, Mac, and Linux.
*   **Access:** You can interact with services by running commands directly in your shell.
*   **Reference:** For specific syntax and examples, refer to the AWS CLI Command Reference.
*   **Configuration:** You can also use the CLI to manage specific service settings, such as configuring EC2Launch v2 (e.g., using `ec2launch collect-logs -o C:\Mylogs.zip`).

### Using AWS SDKs
AWS provides SDKs for various programming languages, which allow you to build applications using language-specific APIs.
*   **Benefits:** SDKs automate tasks such as cryptographically signing requests, retrying requests, and handling error responses.
*   **Implementation:** You can use SDKs to perform complex tasks, such as creating launch templates, managing Auto Scaling groups, or starting instances.
*   **Example (StartInstances):** When using an SDK, you typically create a request object and call the corresponding service method. For example, in .NET, you would create a `StartInstancesRequest` and pass it to `StartInstancesAsync`.
*   **Resources:** You can find libraries, sample code, and tutorials in the AWS Code Examples Repository on GitHub or through the AWS SDKs and Tools Reference Guide.

### Using AWS Tools for PowerShell
These modules are built on the functionality of the SDK for .NET and allow you to script operations on your AWS resources directly from the PowerShell command line. You can find specific cmdlets in the AWS Tools for PowerShell Cmdlet Reference.

### Additional Management Options
*   **CloudFormation:** You can define your infrastructure in JSON or YAML templates to provision and configure resources consistently across regions and accounts.
*   **Programmatic Logic:** When writing code, you can use wrappers (such as the `EC2InstanceWrapper` in Python/Boto3) to encapsulate client interfaces and manage instance actions efficiently.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the provided context. It correctly identifies the three primary programmatic methods (CLI, SDKs, and PowerShell tools) and includes the requested details such as code examples (StartInstances in .NET) and general management concepts (CloudFormation, wrappers). Every claim made is supported by the provided text.

## Caso de prueba 10

**Pregunta de evaluación:**
What is the role of Elastic IP addresses in EC2 and how are they used?

**Respuesta del sistema RAG:**
An Elastic IP (EIP) address is a static, public IPv4 address designed for dynamic cloud computing. Its primary role is to provide a constant IP address that does not change over time, allowing you to mask instance failures by remapping the address to another instance in your account.

### Key Characteristics
*   **Static Nature:** Unlike standard public IPv4 addresses, an Elastic IP remains constant even when you stop and start your instance.
*   **Regional Scope:** An EIP is specific to a single AWS Region and cannot be moved to a different Region.
*   **Network Border Groups:** You must allocate an EIP in the same network border group as the AWS resource you intend to associate it with.
*   **Cost:** AWS charges for all Elastic IP addresses, regardless of whether they are currently associated with a running instance or are idle (unassociated).
*   **Quota:** By default, accounts are limited to five Elastic IP addresses per Region. You can request a quota increase through the Service Quotas console if your architecture requires more.

### How They Are Used
To use an Elastic IP, you must follow a two-step process:

1.  **Allocate:** You first allocate an EIP to your account from Amazon’s pool of IPv4 addresses (or from a custom pool you have brought to AWS).
2.  **Associate:** Once allocated, you associate the EIP with a specific resource, such as an EC2 instance, a network interface, a NAT gateway, or a Network Load Balancer.

**Important Considerations:**
*   **Instance Association:** When you associate an EIP with an instance that already has a public IPv4 address, the original public IP is released back to the Amazon pool and cannot be recovered.
*   **Internet Access:** If you associate an EIP with an instance to enable internet communication, you must ensure the instance resides in a public subnet.
*   **Disassociation:** You can disassociate an EIP from a resource at any time and reassociate it with a different resource. However, the EIP remains allocated to your account (and continues to incur charges) until you explicitly release it.
*   **Best Practices:** AWS recommends using EIPs primarily for their ability to remap addresses during instance failure and suggests using DNS hostnames for other types of inter-node communication.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the information provided in the context chunks. Every claim, including the definition, characteristics, usage process, and best practices, is directly supported by the retrieved text.

## Caso de prueba 11

**Pregunta de evaluación:**
How do IAM roles work with EC2 instances for secure access to AWS services?

**Respuesta del sistema RAG:**
IAM roles allow applications running on EC2 instances to securely make AWS API requests without the need to manually manage or distribute long-term security credentials (such as access keys and secret keys).

Here is how they work:

### 1. Delegation of Permissions
Instead of distributing credentials to each instance, you delegate permissions to the instance by:
*   **Creating an IAM role:** You define which AWS services or accounts can assume the role and specify the API actions and resources the application is permitted to use.
*   **Attaching the role:** You specify the role when launching an instance or attach it to an existing instance. This is done via an **instance profile**, which acts as a container for the IAM role.

### 2. Secure Credential Retrieval
Once a role is attached, applications running on the instance do not need to be hardcoded with credentials. Instead:
*   **Automatic Retrieval:** AWS SDKs, the AWS CLI, and Tools for Windows PowerShell automatically retrieve temporary security credentials from the **Instance Metadata Service (IMDS)**.
*   **Temporary Credentials:** The application retrieves a set of temporary credentials (access key, secret key, and session token) from the IMDS. These credentials are used to sign API requests.
*   **No Manual Management:** Because these credentials are temporary and managed by AWS, you do not need to worry about rotating them or securely distributing them to instances, including those created automatically (e.g., in Auto Scaling groups).

### 3. Best Practices
*   **Least Privilege:** When creating roles, associate policies that restrict access only to the specific API calls and resources your application requires.
*   **Avoid Credential Exposure:** Ensure that services running on your instance (such as HTTP proxies or XML processors) do not expose the credentials retrieved from the metadata service.
*   **Use Instance Profiles:** When using the AWS CLI or API, remember that you must specify the instance profile name, which may differ from the role name if created outside of the console.
*   **Avoid Unnecessary Assumption:** For standard workloads, you do not need to use `sts:AssumeRole` to assume the role already associated with the instance; the instance already provides the necessary temporary session credentials.

### 4. Instance Identity Roles
In addition to the IAM roles you attach, every EC2 instance has an **instance identity role**. This is automatically created at launch and is used by specific AWS services (such as Amazon GuardDuty, AWS Systems Manager, and EC2 Instance Connect) to identify the instance and perform lifecycle or security-related tasks. These credentials are also accessible via the IMDS.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the information provided in the context. Every claim, including the mechanism of IAM roles, the use of instance profiles, the retrieval of credentials via IMDS, the principle of least privilege, and the distinction regarding instance identity roles, is directly supported by the provided text.

## Caso de prueba 12

**Pregunta de evaluación:**
What are the best practices for securing an EC2 instance?

**Respuesta del sistema RAG:**
To secure your Amazon EC2 instances, you should implement a defense-in-depth strategy that covers identity management, network security, storage protection, and ongoing maintenance.

### Identity and Access Management
*   **Use IAM Roles:** Manage access to AWS resources and APIs using identity federation and IAM roles rather than long-term credentials.
*   **Principle of Least Privilege:** Grant users and instances only the minimum set of permissions necessary to perform their functions.
*   **Secure Account Credentials:** Protect your AWS account credentials, use multi-factor authentication (MFA), and set up individual users via IAM or AWS IAM Identity Center.

### Network Security
*   **Security Groups:** Implement the least permissive rules for your security groups. Use them as the primary mechanism for controlling traffic, allowing only known IP addresses and necessary protocols (e.g., HTTPS).
*   **Network ACLs:** Use network ACLs sparingly as a secondary, stateless control to provide high-level subnet guard rails.
*   **Monitoring:** Use VPC Flow Logs to monitor traffic, and utilize tools like Reachability Analyzer or Network Access Analyzer to identify unintended network accessibility.
*   **Secure Connections:** Use EC2 Instance Connect for SSH access to avoid managing SSH keys. Use SSL/TLS (TLS 1.2 or 1.3) for all communications.

### Storage Security
*   **Encryption:** Encrypt all EBS volumes and snapshots.
*   **Data Separation:** Use separate EBS volumes for the operating system and your data to ensure data persistence after instance termination.
*   **Temporary Data:** Use instance store only for temporary data, as it is deleted when an instance is stopped, hibernated, or terminated.

### Maintenance and Monitoring
*   **Patch Management:** Regularly patch and update your operating system and applications. You can automate this process using AWS Systems Manager Patch Manager.
*   **Vulnerability Scanning:** Use Amazon Inspector to automatically discover and scan instances for software vulnerabilities and unintended network exposure.
*   **Threat Detection:** Use Amazon GuardDuty for Malware Protection and Runtime Monitoring to identify suspicious behavior and potential threats.
*   **Compliance Monitoring:** Use AWS Security Hub CSPM controls to monitor your resources against security best practices and standards.
*   **Logging:** Enable API and user activity logging with AWS CloudTrail to audit changes and access.

### Windows-Specific Best Practices
*   **Configuration Baselines:** Establish a secure baseline (e.g., CIS or NIST benchmarks) and use tools like Windows PowerShell DSC to prevent configuration drift.
*   **Host Protection:** Install antivirus, antimalware, and intrusion detection software.
*   **Windows Firewall:** Use Windows Firewall to layer defense-in-depth, and manage settings centrally using Group Policy Objects (GPO).
*   **Administrative Access:** Use Just Enough Administration (JEA) to limit administrative access to the minimum required functions.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately synthesizes the provided context chunks. Every claim made—including identity management, network security, storage, maintenance, and Windows-specific practices—is directly supported by the retrieved documentation. The answer correctly identifies the use of IAM roles, security group best practices, patching, monitoring tools (Inspector, GuardDuty, Security Hub), and specific Windows security features like JEA and GPO, all of which are present in the source text.

## Caso de prueba 13

**Pregunta de evaluación:**
How does EBS (Elastic Block Store) integrate with EC2 and what are its volume types?

**Respuesta del sistema RAG:**
Amazon Elastic Block Store (EBS) integrates with Amazon EC2 by providing durable, block-level storage volumes that can be attached to and detached from your instances. 

### Integration with EC2
*   **Persistence:** Unlike instance store volumes, EBS volumes persist independently of the life of the associated EC2 instance.
*   **Attachment:** You can attach multiple EBS volumes to an instance. You can perform these attachments during instance launch or at any time after the instance is running.
*   **Performance:** EBS performance is bounded by the instance type's limits or the aggregated performance of the attached volumes. For optimal performance, you can use EBS-optimized instances.
*   **Management:** You can increase the size or performance of EBS volumes without detaching them or restarting the instance.
*   **Backups:** You can create snapshots of your EBS volumes, which are stored in Amazon S3. These snapshots can be used to create new volumes, migrate data across AWS Regions or accounts, or automate backups using AWS Backup or Amazon Data Lifecycle Manager.
*   **Security:** You can encrypt your EBS volumes. If you choose to encrypt a volume, you must select a customer-managed key (or use the default if configured).

### Volume Types
Regarding specific volume types, the provided documentation notes that you can select from various types when configuring your instance, and the available options depend on the instance type chosen. Specifically, the documentation mentions:
*   **General Purpose SSD volumes**
*   **Provisioned IOPS SSD volumes** (such as `io1`, `io2`, and `gp3`)
*   **Other types** (such as `gp2`, `st1`, `sc1`, and standard volumes)

For detailed specifications regarding these volume types, the documentation refers users to the *Amazon EBS User Guide*.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately describes the integration of EBS with EC2 based on the provided text, including persistence, attachment, performance, management, backups, and security. It also correctly identifies the volume types mentioned in the context (General Purpose SSD, Provisioned IOPS SSD, and others like st1/sc1) while noting that the specific details are found in the external 'Amazon EBS User Guide', which is consistent with the provided text's references.

## Caso de prueba 14

**Pregunta de evaluación:**
What is eventual consistency in EC2 and how can it affect API operations?

**Respuesta del sistema RAG:**
In Amazon EC2, **eventual consistency** refers to the fact that when you create or modify a resource, the change may not be immediately visible to subsequent API calls. Because it takes time for resource information to propagate throughout the system, a command run immediately after a creation request might fail because the system does not yet recognize the new resource ID.

### How it affects API operations
Eventual consistency can lead to errors when you perform operations in rapid succession. Common examples include:

*   **InvalidInstanceID.NotFound:** If you run `DescribeInstances` immediately after `RunInstances`, the system may return this error even though the instance was successfully created.
*   **InvalidGroup.NotFound:** Similarly, if you call `DescribeSecurityGroups` immediately after `CreateSecurityGroup`, the system may not yet recognize the new security group ID.
*   **Resource State Uncertainty:** When you terminate an instance, a subsequent `TerminateInstances` call might return an error, even if the instance is still running, because the system state has not fully updated.

### How to manage eventual consistency
To handle these scenarios and ensure your applications function reliably, you should implement the following practices:

1.  **Use Exponential Backoff:** When you receive an error indicating a resource is not found, do not assume the operation failed. Instead, run the appropriate `Describe` command repeatedly using an exponential backoff algorithm. Start with a wait time of a few seconds and gradually increase it up to a few minutes to allow time for the resource information to propagate.
2.  **Confirm State Before Modification:** Always confirm the current state of a resource using a `Describe` command before attempting to modify or terminate it.
3.  **Add Wait Time:** Even if a `Describe` command returns a successful response, it is recommended to add wait time between subsequent commands using an exponential backoff strategy to ensure the system is fully synchronized.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the information provided in the context. It correctly defines eventual consistency in the context of EC2, provides the specific examples of API errors mentioned in the text (InvalidInstanceID.NotFound, InvalidGroup.NotFound), and outlines the recommended strategies for handling these issues, such as using exponential backoff and confirming resource states.

## Caso de prueba 15

**Pregunta de evaluación:**
How can I monitor EC2 API usage and set up CloudWatch alarms for throttling events?

**Respuesta del sistema RAG:**
To monitor Amazon EC2 API requests and manage throttling, you can use Amazon CloudWatch. Note that Amazon EC2 API metrics is an opt-in feature, and you must request access to it via the AWS Support Center before you can use it.

### Monitoring API Usage and Throttling
Once enabled, CloudWatch collects raw data on your API operations, allowing you to track usage and identify issues. You can use these metrics to monitor API throttling specifically.

### Setting Up CloudWatch Alarms for API Errors
You can create CloudWatch alarms to notify you when API request failures (such as those caused by server-side errors or throttling) reach a specific threshold.

**Steps to create an alarm for API request errors:**
1. Open the **CloudWatch console**.
2. In the navigation pane, choose **Alarms** > **All alarms**.
3. Choose **Create alarm**.
4. Choose **Select metric** and configure the following:
   - Select **EC2/API**.
   - Choose **Per-Action Metrics**.
   - Select the check box for the specific API action (e.g., `DescribeInstances`) that corresponds to the `ServerErrors` metric.
   - Choose **Select metric**.
5. On the **Specify metric and conditions** page:
   - Under **Metric**, set the **Statistic** to **Sum** and verify the **Period** is set to 5 minutes.
   - Under **Conditions**, define the threshold (e.g., 10 server-side errors) that should trigger the alarm.
6. Configure the **Alarm notification** to send an Amazon SNS message when the alarm changes state.

For general information on API limits, you can refer to the resource token bucket sizes and refill rates provided in the documentation, which help you understand the thresholds for various API actions like `RunInstances` or `TerminateInstances`.

**Evaluación del juez:**
- **score**: 5
- **reasoning**: The answer accurately reflects the provided context. It correctly identifies that EC2 API metrics are an opt-in feature requiring a request via the AWS Support Center. It provides the correct steps for creating a CloudWatch alarm for API errors (specifically referencing the EC2/API namespace and Per-Action Metrics) as outlined in the documentation. It also correctly mentions the resource token bucket sizes and refill rates as a reference for understanding API limits.

## Resultado final: 5.0/5