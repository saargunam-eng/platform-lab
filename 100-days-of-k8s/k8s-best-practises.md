# Kubernetes Best Practices

## Workload Configuration

### Always set resource requests and limits:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    memory: "256Mi"   # set memory limit; CPU limit is optional (throttle vs kill)
```

### Always define health checks:

```yaml
readinessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 20
  failureThreshold: 3
```

### Set a PodDisruptionBudget for every production Deployment:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: api
```

## Image and Container Hygiene

* Never use latest tag - pin to a specific digest or semantic version (`myapp:v1.4.2`)
* Run as non-root: `securityContext.runAsNonRoot: true`
* Read-only root filesystem: `securityContext.readOnlyRootFilesystem: true`
* One process per container - don't run multiple services in one container

## Namespace and Label Strategy

```yaml
metadata:
  labels:
    app: api               # selector for Services, NetworkPolicies
    version: v1.4.2        # for blue-green
    team: platform         # for quota attribution
    environment: production
```

Separate teams into namespaces with ResourceQuotas and LimitRanges per namespace.

## Deployment Configuration

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # add 1 new pod before removing old
      maxUnavailable: 0    # never reduce capacity during rollout
  template:
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: api
```

`topologySpreadConstraints` prevents all pods from landing in the same AZ.

## What to Avoid

| ANTI-PATTERN | WHY IT'S BAD | ALTERNATIVE |
| --- | --- | --- |
| latest image tag | Unpredictable deployments | Pin to digest |
| No resource requests | Pods evicted under pressure | Always set requests |
| Secrets in ConfigMaps | Secrets exposed in plaintext | Use Secrets or External Secrets Operator |
| Running as root | Container escape = node compromise | `runAsNonRoot: true` |
| Single replica for stateless services | Single point of failure | Minimum 2 replicas |
| `kubectl apply` in production CI | No audit trail, no rollback | GitOps with ArgoCD/Flux |
