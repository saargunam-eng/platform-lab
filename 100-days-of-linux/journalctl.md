# journalctl: Querying the systemd Journal for Service Debugging

`journalctl` is the CLI for querying `journald`, the `systemd` journal daemon. Unlike traditional `syslog`, `journald` stores logs in a structured binary format with indexed fields, enabling fast filtered queries across all system units, the kernel, and boot sequences. This makes it significantly more powerful than grepping through flat log files.

## Core Usage Patterns

**Follow live logs for a specific unit:**

```bash
journalctl -u nginx.service -f
```

**Limit to recent timeframes:**

```bash
journalctl -u nginx.service --since today
journalctl -u nginx.service --since "2026-06-01 14:00:00" --until "2026-06-01 15:30:00"
```

**Show only errors and above across all units:**

```bash
journalctl -p err..emerg
```

Priority levels follow `syslog` convention: `emerg`, `alert`, `crit`, `err`, `warning`, `notice`, `info`, `debug`. The range syntax `err..emerg` filters to error severity and above.

## Diagnosing Crashes and Reboots

When a service failure causes a reboot or kernel panic, the current boot's journal won't contain the failure. Use boot indexing:

```bash
# List available boots
journalctl --list-boots

# Current boot
journalctl -b

# Previous boot - critical for post-crash analysis
journalctl -b -1

# Two boots ago
journalctl -b -2
```

On AWS EC2, if an instance rebooted unexpectedly (OOM killer, kernel panic), `journalctl -b -1 -p err..emerg` immediately surfaces the cause without needing to dig through rotated log files.

## Structured Field Filtering

`journald` indexes every log entry by structured fields. You can filter on any combination:

```bash
# Filter by unit and PID simultaneously
journalctl _SYSTEMD_UNIT=gunicorn.service _PID=28471

# Filter by executable path
journalctl _EXE=/usr/bin/python3

# Filter by systemd slice (useful for cgroup-based resource debugging)
journalctl _SYSTEMD_SLICE=app.slice
```

The underscore prefix denotes trusted journal fields set by `journald` itself, not the logging process. These cannot be spoofed by the application.

## Piping and Programmatic Output

**Disable pagination for piping to other tools:**

```bash
journalctl -u postgres.service --no-pager | grep "FATAL"
journalctl -u postgres.service --no-pager --since "1 hour ago" | grep -E "ERROR|FATAL" | tail -50
```

**For alerting pipelines or log shipping, output structured JSON:**

```bash
journalctl -u myapp.service -o json | jq '.MESSAGE'
journalctl -u myapp.service -o json-pretty | jq 'select(.PRIORITY <= "3")'
```

This is particularly useful when shipping logs to CloudWatch Logs or Elasticsearch from a script, since you can extract specific fields without text parsing.

## Practical Debugging Workflow

A typical workflow for a failed `systemd` service on a production EC2 instance:

```bash
# 1. Check service status and last log lines
systemctl status myapp.service

# 2. Pull full logs for this boot with timestamps
journalctl -u myapp.service -b --no-pager

# 3. If the unit failed on a previous boot
journalctl -u myapp.service -b -1

# 4. Cross-reference kernel messages around the failure time
journalctl -k --since "2026-06-02 09:00:00" --until "2026-06-02 09:05:00"

# 5. Check for OOM kills specifically
journalctl -k | grep -i "oom\|killed process"
```

## Journal Size and Retention

On long-running instances, the journal can grow large. 

**Key config in `/etc/systemd/journald.conf`:**

```ini
SystemMaxUse=2G
SystemKeepFree=500M
MaxRetentionSec=30day
```

**Check current disk usage:**

```bash
journalctl --disk-usage
```

**Force rotation and vacuum old entries:**

```bash
journalctl --vacuum-size=1G
journalctl --vacuum-time=14d
```

## Key Takeaway

`journalctl` replaces the pattern of `tail -f /var/log/app.log` with a queryable, structured log store. The combination of boot indexing (`-b -1`), priority filtering (`-p err..emerg`), and field-based queries (`_SYSTEMD_UNIT`, `_PID`) makes it the fastest path to root cause on any `systemd`-based Linux system - whether debugging a crashed FastAPI service on EC2 or a failing kubelet on a Kubernetes node.
