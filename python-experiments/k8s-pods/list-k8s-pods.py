from kubernetes import client, config

# Load configuration from default location (~/.kube/config)
config.load_kube_config()

# Initialize the CoreV1Api
v1 = client.CoreV1Api()

print("Listing pods with their IPs and Status:")
# List pods across all namespaces
ret = v1.list_pod_for_all_namespaces(watch=False)

for i in ret.items:
    print(f"Namespace: {i.metadata.namespace} \t Name: {i.metadata.name} \t IP: {i.status.pod_ip} \t Status: {i.status.phase}")
