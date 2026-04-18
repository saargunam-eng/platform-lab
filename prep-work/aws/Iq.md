# AWS Interview Questions & Scenarios

### Q: You have a web server hosted in EC2, and you wish to retain the IP address of the instance in all scenarios — instance terminated, rebooted, or stopped. How would you find the IP address?
**A:** Use an Elastic IP (EIP). Allocate an EIP from AWS and associate it with your EC2 instance. Unlike a public IP (which changes on stop/start), an EIP stays in your account permanently. If the instance is terminated, spin up a new one and re-associate the same EIP — your IP never changes.

---

### Q: Is there any default limit which comes with Elastic IPs?
**A:** Yes. AWS allows 5 EIPs per region per account by default. You can request an increase via the Service Quotas console. 
*Note: AWS charges you for EIPs that are allocated but not associated with a running instance — so release unused EIPs.*

---

### Q: Can we attach multiple EIPs to the same instance?
**A:** Yes, indirectly. You can attach multiple ENIs (Elastic Network Interfaces) to an instance (limit depends on instance type), and each ENI can have one EIP. So one instance can have multiple EIPs — one per ENI.

---

### Q: Can we reuse the same EIP?
**A:** Yes. An EIP stays in your account until you explicitly release it. You can disassociate it from one instance and associate it with another anytime. That's the whole purpose — portability of IP.

---

### Q: If you wish to take a backup of the same server with its data and entire config, how will you take that? Is read-replica a cost-effective solution?
**A:** Use AMI (Amazon Machine Image). An AMI captures everything — OS, installed software, configurations, and all attached EBS volumes. You can launch an identical instance from it anytime.

Read replicas are not for backup — they're for read scaling in RDS. Using them as backup is neither the right tool nor cost-effective. EBS Snapshots + AMI is the correct and cost-effective approach. Snapshots are incremental after the first one, so storage costs are low.

---

### Q: Is there any other solution using ELB?
**A:** ELB (Elastic Load Balancer) has nothing to do with backups. It distributes traffic across instances for availability. It does not back up data or instance config. This is a common misconception — ELB = traffic management, not backup.

---

### Q: How will you avoid redundancy in the snapshot mechanism?
**A:** Use AWS Data Lifecycle Manager (DLM) or AWS Backup. These let you define retention policies — for example: keep daily snapshots for 7 days, weekly for 30 days, monthly for 1 year. Old snapshots are automatically deleted. Tag your resources properly so policies apply to the right volumes.

---

### Q: Your EC2 instance requires connectivity to multiple subnets (public/private). How will you set this up?
**A:** Attach multiple ENIs to the instance — one per subnet. For example:
- **ENI 1** in a public subnet with an EIP → internet-facing traffic
- **ENI 2** in a private subnet → internal service communication

Configure the OS routing table (`ip route`) to route traffic through the correct ENI based on destination. Security groups are applied per ENI independently.

---

### Q: Your EC2 wants to access resources in S3. How do you set access control using IAM?
**A:** Create an IAM Role with an S3 policy (e.g., `s3:GetObject`, `s3:PutObject`). Attach the role to the EC2 instance as an Instance Profile. The instance automatically gets temporary credentials via the metadata service (IMDS). Never hardcode access keys on the instance.

---

### Q: Do you need to make changes at the security group level for S3 access?
**A:** No. S3 is a managed AWS service — security groups don't apply to it. What controls access is:
1. IAM Role policy on the EC2
2. S3 Bucket policy
3. *(Optional)* VPC Gateway Endpoint for S3 — keeps traffic on AWS's private network, avoiding the internet entirely. Recommended for production.

---

### Q: What if your S3 is in a different account?
**A:** Two things are required:
1. **S3 Bucket Policy** in the target account must explicitly allow the source account's IAM role ARN.
2. **IAM Role** in the source account must have permission to access the target bucket.

*Optional:* Use STS AssumeRole — EC2 assumes a role in the target account and uses those temporary credentials to access S3.

---

### Q: How will you handle inbound traffic — any port allowed or any IP?
**A:** Never open `0.0.0.0/0` on sensitive ports. Follow this pattern:
- **Port 443** — open to `0.0.0.0/0` at the load balancer only
- **Port 22 (SSH)** — restricted to bastion host SG or specific corporate IP CIDR
- **App ports** — only between specific security groups (ALB SG → App SG → DB SG)
- Enable **VPC Flow Logs** to audit all traffic

---

### Q: You're managing an AWS Organization with 1000 AWS accounts. How will you create a seamless environment to manage users and accounts?
**A:** Use this stack:
- **AWS Organizations** — group accounts into OUs (prod, non-prod, security, shared-services)
- **Service Control Policies (SCPs)** — enforce guardrails at OU level (e.g., deny resources outside approved regions)
- **AWS Control Tower** — automates account vending, landing zone setup, centralized logging
- **AWS IAM Identity Center (SSO)** — integrates with corporate IdP (Okta, Azure AD). Users log in once and get federated access to all accounts with appropriate permission sets. No individual IAM users per account.

---

### Q: How will you handle the authentication part?
**A:** Use **IAM Identity Center + corporate IdP** (e.g., Okta, Azure AD) via SAML 2.0 or OIDC federation. 
- Users authenticate against the corporate directory. 
- MFA enforced at the IdP level. 
- Permission sets in IAM Identity Center map to IAM roles in each account. 
- No standing credentials — all access is via temporary STS tokens.

---

### Q: You're handling a gaming application with massive concurrent users. Which load balancer will you pick, where will you place it, and what security measures will you take?
**A:** 
**Load Balancer:**
- **Network Load Balancer (NLB)** — gaming uses UDP/TCP for real-time low-latency communication. NLB handles millions of connections with ultra-low latency. *(If HTTP-based REST/WebSocket, use ALB).*

**Architecture placement:**
- NLB at the edge (public subnet)
- Game servers in private subnets (Auto Scaling Group)
- Separate fleet for matchmaking, auth, leaderboard services

**Security measures:**
- **AWS Shield Standard (free)** — always on DDoS protection
- **AWS Shield Advanced** — for high-value gaming targets, includes 24/7 DRT support
- **WAF on ALB/CloudFront** — rate limiting, geo-blocking, IP reputation lists
- **Security Groups** — restrict ports to only what the game uses
- **Encryption in transit (TLS)** for all non-UDP game traffic
- **VPC isolation** — game servers never directly exposed to internet
