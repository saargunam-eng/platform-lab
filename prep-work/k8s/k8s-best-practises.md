# What Are Some Kubernetes Best Practices?

Most engineers can get a Kubernetes cluster running. The gap shows up in production: pods get OOMKilled at 2am, when a bad deploy takes down more than it should, or when the security team asks who has cluster-admin and nobody has a clean answer. Kubernetes best practices exist precisely to close that gap before it becomes an incident.

This post covers 8 Kubernetes best practices that actually matter in production, with enough context to use them in an interview answer and apply them the next morning.

## Quick Answer: 8 Kubernetes Best Practices at a Glance

| # | Best Practice | Why It Matters |
|---|---|---|
| 1 | Set resource requests and limits | Prevents noisy-neighbour crashes and OOM kills |
| 2 | Use namespaces to separate environments | Isolates teams and workloads, enables RBAC scoping |
| 3 | Configure liveness and readiness probes | Ensures traffic only reaches healthy pods |
| 4 | Apply RBAC with least privilege | Limits blast radius of compromised credentials |
| 5 | Never run containers as root | Reduces container escape risk |
| 6 | Use ConfigMaps and Secrets correctly | Keeps config separate from code and images |
| 7 | Set up Horizontal Pod Autoscaler | Handles load spikes without manual intervention |
| 8 | Define Pod Disruption Budgets | Maintains availability during node maintenance |

## Kubernetes Best Practices Explained

### 1. Set Resource Requests and Limits
Every container in your cluster should define resource requests and limits for CPU and memory. Requests tell the scheduler how much resource to reserve for the pod when placing it on a node. Limits cap what it can consume at runtime.

Without limits, a single misbehaving pod can consume all memory on a node and bring down every other workload sharing it. Without requests, the scheduler places pods blindly and you end up with heavily loaded nodes sitting next to nearly idle ones.

A good starting point: set requests conservatively based on observed usage, set limits at roughly 2x the request for CPU (which is compressible) and tighter for memory, since exceeding the memory limit triggers an OOMKill. Review with tools like Goldilocks or Vertical Pod Autoscaler in recommendation mode.

### 2. Use Namespaces to Separate Environments
Namespaces are the primary unit of isolation in Kubernetes. At minimum, separate your production, staging, and development workloads into distinct namespaces. In larger organisations, give each team their own namespace.

This matters because RBAC policies, resource quotas, and network policies are all scoped to namespaces. If your developers have deployment access to dev but not production, that’s enforced at the namespace level. Without this separation, a misapplied `kubectl` command against the wrong context can affect production, and it happens more often than people admit.

Pair namespaces with `ResourceQuota` objects to prevent any single team from consuming disproportionate cluster resources.

### 3. Configure Liveness and Readiness Probes
These two health check probes are different things that solve different problems, and confusing them causes subtle production issues.

A **readiness probe** tells Kubernetes whether a pod is ready to receive traffic. If it fails, the pod is removed from the Service endpoints but keeps running. Use this to handle slow startup times or temporary dependency outages. Your pod stays up but gets taken out of rotation until it recovers.

A **liveness probe** tells Kubernetes whether a pod is alive. If it fails repeatedly, Kubernetes restarts the container. Use this for detecting deadlocks or stuck states that the application itself cannot recover from.

A common mistake is setting liveness probe thresholds too aggressively, causing restart loops during legitimate slow startups. For slow-starting apps, add a `startupProbe` to give the container time to initialise before liveness kicks in.

### 4. Apply RBAC with Least Privilege
Kubernetes RBAC controls who can do what in your cluster. The default mistake is over-permissioning: giving developers cluster-admin because it’s easy, or letting CI/CD pipelines run with wildcard permissions.

In practice, define roles that match actual job functions. A developer deploying to their namespace needs `get`, `list`, `create`, and `update` on Deployments in that namespace. They don’t need access to Secrets in other namespaces, or to modify ClusterRoles. Use RoleBinding for namespace-scoped access and ClusterRoleBinding only where genuinely needed.

For CI/CD pipelines, create a dedicated ServiceAccount with the minimum permissions required for that pipeline’s job. Audit RBAC permissions regularly, as they accumulate over time and rarely get cleaned up. For multi-account environments where Kubernetes clusters sit alongside other AWS services, this connects directly to multi-account access management principles.

### 5. Never Run Containers as Root
By default, many container images run as root (UID 0). If an attacker exploits a vulnerability in your application, running as root means they potentially have root on the container, and container escapes, while uncommon, do happen.

Set `runAsNonRoot: true` and specify a `runAsUser` in your pod’s `securityContext`. Also set `readOnlyRootFilesystem: true` where your application allows it, and drop unnecessary Linux capabilities with `capabilities.drop: [ALL]`.

These settings can be enforced cluster-wide using Pod Security Admission (the replacement for the deprecated PodSecurityPolicy), so teams can’t accidentally ship containers without them.

### 6. Use ConfigMaps and Secrets Correctly
ConfigMaps store non-sensitive configuration. Secrets store sensitive values like passwords, tokens, and certificates. The most important Kubernetes best practice here is not to mix them up and not to bake configuration into container images.

Kubernetes Secrets are base64-encoded by default, which is encoding, not encryption. For production, enable encryption at rest for etcd and use an external secrets manager like AWS Secrets Manager or HashiCorp Vault, synced into the cluster via the External Secrets Operator. This ensures secrets are never stored in plaintext in etcd or committed to Git.

For container workloads on EKS specifically, understanding how this integrates with IAM roles for service accounts is essential, covered in detail in the ECS vs EKS comparison.

### 7. Set Up Horizontal Pod Autoscaler
The Horizontal Pod Autoscaler (HPA) automatically scales your deployment’s replica count based on observed CPU, memory, or custom metrics. Without it, you’re either over-provisioning replicas to handle peak load (wasteful) or manually scaling during incidents (slow and stressful).

A basic HPA targeting 60% CPU utilisation works well as a starting point for most stateless services. For more sophisticated scaling, for example based on queue depth or request rate, the KEDA project extends HPA with custom event-driven triggers.

One thing to get right: HPA only works properly when resource requests are set correctly (best practice 1). The HPA calculates utilisation as actual usage divided by requested amount. If requests aren’t set, HPA has nothing to calculate against and won’t scale. These two practices are interdependent.

### 8. Define Pod Disruption Budgets
A Pod Disruption Budget (PDB) tells Kubernetes the minimum number (or percentage) of pods that must remain available during voluntary disruptions, including node drains during upgrades, cluster autoscaler scale-downs, or rolling deployments.

Without a PDB, a node drain can evict all pods of a deployment simultaneously if they happen to be on the same node. With a PDB of `minAvailable: 1`, Kubernetes will not evict the last remaining pod, preserving availability throughout the maintenance window.

This is a commonly missed practice. Teams configure HPA and multi-AZ deployments for high availability but skip PDBs, then hit unexpected downtime during their first cluster upgrade.

## Example Interview Answer

Here’s how to structure your response when asked about Kubernetes best practices:

> “There are several Kubernetes best practices I apply consistently in production. On the reliability side: always set resource requests and limits to prevent noisy-neighbour issues, configure readiness and liveness probes so traffic only hits healthy pods, and define Pod Disruption Budgets to protect availability during maintenance.
> 
> On security: I enforce RBAC with least privilege: separate service accounts for each workload, no cluster-admin unless strictly necessary. Containers run as non-root with read-only file systems where possible, and secrets go through an external secrets manager rather than being stored directly in etcd.
> 
> For scalability, I set up HPA tied to CPU or custom metrics so the cluster scales automatically rather than someone paging me at 11pm. And I always use namespaces to isolate teams and environments so resource quotas and policies can be applied cleanly per team.”

## Common Mistakes to Avoid

- **Skipping resource requests and limits entirely.** It’s the most common production Kubernetes mistake. New clusters feel stable without them until traffic spikes, a memory leak runs unchecked, and the node goes down taking unrelated workloads with it.
- **Using cluster-admin for everything.** It’s quick during setup and never gets cleaned up. Audit your `ClusterRoleBindings` regularly, and you’ll likely find service accounts with more access than they need.
- **Confusing readiness and liveness probes.** Using a liveness probe where you need a readiness probe causes unnecessary restarts. A pod that’s temporarily unable to connect to a database doesn’t need to be restarted. It needs to be taken out of rotation until the connection recovers.
- **Treating base64 as encryption.** Kubernetes Secrets are not encrypted by default. Assuming they are is a security gap. Enable etcd encryption at rest and use an external secrets manager for anything sensitive.
- **Forgetting Pod Disruption Budgets before cluster upgrades.** The first cluster upgrade without PDBs configured is usually the lesson that makes teams add them. Don’t learn it the hard way.

## Key Takeaway

Kubernetes best practices fall into three categories: **stability** (resource limits, probes, PDBs), **security** (RBAC, non-root containers, proper secrets management), and **scalability** (HPA, namespace isolation). The strongest interview answers pick two or three from each category, explain why they matter, and connect them to something real: an incident prevented, a cost saved, or a compliance requirement met. That’s the difference between reciting a list and demonstrating experience.