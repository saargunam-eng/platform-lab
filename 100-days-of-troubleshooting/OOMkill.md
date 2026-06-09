# Why Your Pod OOMKills Despite Low Apparent Memory Usage

Your Kubernetes pods are being `OOMKilled` repeatedly despite the application appearing to run fine locally. The memory limit is set to `512Mi` but the process only uses `200MB`. How do you explain and fix this?

The core issue: the Linux OOM killer measures all memory mapped to the cgroup, not just your application's heap. When the kernel enforces the `512Mi` cgroup limit, it counts heap, stack, code segments, shared libraries, memory-mapped files, and the kernel page cache accumulated from file I/O. Your local machine has gigabytes of RAM to absorb this overhead; the container does not.

---

## Diagnosing the Problem

**Step 1 - Confirm OOMKill is the cause**

```bash
kubectl describe pod <pod-name> -n <namespace>
# Look for:
# Last State: Terminated
#   Reason: OOMKilled
#   Exit Code: 137
```

Exit code 137 = `SIGKILL` (128 + 9), sent by the kernel OOM killer.

**Step 2 - Watch memory over time**

```bash
kubectl top pod <pod-name> --containers -n <namespace>
# Run this every 10 seconds leading up to the crash
watch -n 10 kubectl top pod <pod-name> -n <namespace>
```

**Step 3 - Inspect memory breakdown inside the container**

```bash
kubectl exec -it <pod-name> -- cat /proc/<pid>/status | grep -E 'VmRSS|VmPeak|VmSwap|VmData'
# VmRSS  = current resident set size (physical RAM in use)
# VmPeak = high watermark - this often exceeds your "steady state" reading
```

Also check cgroup accounting directly:

```bash
kubectl exec -it <pod-name> -- cat /sys/fs/cgroup/memory/memory.usage_in_bytes
kubectl exec -it <pod-name> -- cat /sys/fs/cgroup/memory/memory.stat
# Look at: cache, rss, mapped_file
```

The `cache` line in `memory.stat` is often the surprise - aggressive file I/O (reading config files, JAR loading, module imports) fills the page cache and pushes cgroup usage past the limit.

---

## JVM Applications

The JVM heap ( `-Xmx` ) is only part of the footprint. Off-heap memory includes:

- **Metaspace** (class metadata) - can grow unbounded by default
- **Code cache** (JIT compiled code)
- **Direct byte buffers** (NIO, Netty)
- **Thread stacks** (each thread defaults to 512KB-1MB)

Rule of thumb: set `-Xmx` to 60-70% of the container memory limit.

For a `512Mi` limit, set:

```bash
-Xmx320m -Xms320m -XX:MaxMetaspaceSize=96m -XX:ReservedCodeCacheSize=64m
```

In Kubernetes:

```yaml
env:
  - name: JAVA_OPTS
    value: "-Xmx320m -Xms320m -XX:MaxMetaspaceSize=96m -XX:ReservedCodeCacheSize=64m -XX:+UseContainerSupport"
resources:
  requests:
    memory: "512Mi"
  limits:
    memory: "512Mi"
```

`-XX:+UseContainerSupport` (default in JDK 10+) makes the JVM read cgroup limits instead of host RAM. Without it, the JVM sizes its heap relative to the node's 64GB RAM.

---

## Node.js Applications

V8's default old-space heap limit is derived from the host machine's physical RAM - not the container limit. On a 64GB node, V8 may allow up to ~1.5GB of heap before GCing aggressively.

Fix with an explicit flag:

```dockerfile
CMD ["node", "--max-old-space-size=384", "server.js"]
```

Or via environment variable (Node 18+):

```yaml
env:
  - name: NODE_OPTIONS
    value: "--max-old-space-size=384"
```

For a `512Mi` container limit, `384MB` leaves roughly `128MB` for V8 overhead, OS, and native modules.

---

## The Fix: Memory Settings + Request/Limit Configuration

Set memory request equal to limit to get Kubernetes `Guaranteed` QoS class. This prevents the pod from being scheduled onto a node without enough free memory, and it protects the pod from being evicted under node pressure before it even hits the cgroup limit.

```yaml
resources:
  requests:
    memory: "512Mi"   # same as limit = Guaranteed QoS
  limits:
    memory: "512Mi"
```

If tuning runtime settings is not enough, increase the limit to reflect the true footprint:

```bash
# Use VmPeak from /proc/<pid>/status as your baseline
# Add 20-30% headroom for page cache and burst allocations
# Round up to the nearest 128Mi boundary
```

For ongoing visibility, deploy the Kubernetes Metrics Server and set up a HorizontalPodAutoscaler or a simple Prometheus alert on `container_memory_working_set_bytes / container_spec_memory_limit_bytes > 0.85` to catch growth before the next OOMKill.
