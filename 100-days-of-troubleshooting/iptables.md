# Scenario: "Kampot": A New Port (Easy)

## Problem Statement
A Python bank-simulation application runs on Debian 13 as root, listening exclusively on port `20280`. It cannot be reconfigured or stopped. An internal legacy monitoring tool requires the service to be accessible locally on port `80`.

## Production-Grade Solution (Interview-Ready)
The most efficient, zero-overhead method is using kernel-level packet redirection via `iptables`.

### 1. Apply Redirection Rules
```bash
# Redirects traffic coming from external networks
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 20280

# Redirects traffic originating locally (e.g., localhost/127.0.0.1)
sudo iptables -t nat -A OUTPUT -p tcp -o lo --dport 80 -j REDIRECT --to-ports 20280
```

### 2. Interview Breakdown (How to Explain It)
* **`-t nat`**: Modifies the Network Address Translation table.
* **`PREROUTING` vs `OUTPUT`**: `PREROUTING` intercepts inbound external traffic; `OUTPUT` intercepts outbound local loops (like `curl localhost`).
* **`-j REDIRECT --to-ports`**: Reroutes the packet destination at the Linux kernel level without requiring proxy software.

### 3. Verification & Submission
```bash
# Test the redirection
curl localhost:80/accounts

# Validate the solution for the challenge
/home/admin/agent/check.sh
```
