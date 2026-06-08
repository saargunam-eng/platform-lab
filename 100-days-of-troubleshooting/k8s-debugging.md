# Debugging Pod Restart Loops in Kubernetes

Pod restarts (`CrashLoopBackOff` or high `RESTARTS` count) mean the container is starting, crashing, and Kubernetes is restarting it with exponential backoff. The container itself is the source of truth.

## Step 1: Identify the scope

```bash
# Which pods are restarting?
kubectl get pods -A --sort-by='.status.containerStatuses[0].restartCount' | tail -20

# Get details on the specific pod
kubectl describe pod <pod-name> -n <namespace>
```

In `kubectl describe`, look for:

- **Last State:** shows the previous container's exit code and reason
- **Reason:** `OOMKilled`, `Error`, `Completed`
- **Events:** recent events (image pull errors, probe failures, scheduling issues)

Exit codes tell you a lot:

| EXIT CODE | MEANING |
| --- | --- |
| 0 | Container exited cleanly (job finished, not a crash) |
| 1 | Application error (unhandled exception, bad config) |
| 137 | OOMKilled (killed by OS due to memory limit) |
| 139 | Segfault |
| 143 | SIGTERM not handled (graceful shutdown failure) |

## Step 2: Read the logs

```bash
# Current container logs
kubectl logs <pod-name> -n <namespace>

# Previous container logs (the one that crashed)
kubectl logs <pod-name> -n <namespace> --previous

# Follow logs in real time to catch the crash
kubectl logs <pod-name> -n <namespace> -f

# If the pod has multiple containers
kubectl logs <pod-name> -n <namespace> -c <container-name> --previous
```

The `--previous` flag is the most useful - it shows what the container printed before it died.

## Step 3: Common causes and fixes

**OOMKilled (exit 137):** The container exceeded its memory limit. Kubernetes killed it.

```bash
# Confirm with describe
kubectl describe pod <pod-name> | grep -A5 "Last State"
# Reason: OOMKilled

# Check current memory usage vs limits
kubectl top pod <pod-name> -n <namespace>
```

Fix: increase the memory limit or fix a memory leak:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"  # increase this if OOMKilled
    cpu: "500m"
```

**Application crash (exit 1):** Your code is throwing an exception on startup. Check `--previous` logs for the stack trace. Common causes:

- Missing environment variable or secret
- Cannot connect to database at startup
- Config file not found
- Port already in use

**Liveness probe failure:** If the liveness probe fails, Kubernetes restarts the pod even if the container is still running:

```bash
kubectl describe pod <pod-name> | grep -A10 "Liveness"
# "Liveness probe failed: ..."
```

Fix: make the probe path reliable and set appropriate thresholds:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30  # give the app time to start
  periodSeconds: 10
  failureThreshold: 3      # 3 consecutive failures before restart
  timeoutSeconds: 5
```

Do not check external dependencies (DB, Redis) in the liveness probe - if the DB is briefly unavailable, you do not want all pods restarting at once.

**Image pull failure:**

```bash
kubectl describe pod <pod-name> | grep -A5 "Warning"
# Failed to pull image "123456.dkr.ecr.ap-south-1.amazonaws.com/app:v1.2"
```

Causes: wrong image tag, ECR permissions missing, network issue. Fix IAM role permissions for the node group or the pod's service account.

**Resource pressure on the node:**

```bash
# Is the node under pressure?
kubectl describe node <node-name> | grep -A10 "Conditions"
# MemoryPressure, DiskPressure, PIDPressure = True is bad

# What pods are on this node?
kubectl get pods -A --field-selector spec.nodeName=<node-name>
```

If the node is under pressure, the kubelet may be evicting pods. Fix: drain and cordon the node, let the ASG replace it.

## Step 4: Temporarily increase verbosity

Add debug logging to the container environment:

```yaml
env:
  - name: LOG_LEVEL
    value: "DEBUG"
  - name: PYTHONFAULTHANDLER
    value: "1"  # Python: dump traceback on crash
```

## Step 5: Prevent restarts during investigation

If you need the pod to stay up for investigation, change `restartPolicy` temporarily or use a debug sidecar:

```bash
# Override the command to keep the container alive
kubectl run debug-pod   --image=123456.dkr.ecr.ap-south-1.amazonaws.com/app:v1.2   --command -- sleep infinity

# Then exec in and run the app manually to see what happens
kubectl exec -it debug-pod -- bash
```

This bypasses the normal entrypoint so you can inspect the filesystem and run commands interactively.