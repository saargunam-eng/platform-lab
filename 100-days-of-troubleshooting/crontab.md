# Scenario: "Alexandria": The Vanishing Backups (Easy)

## Problem Statement
A critical daily backup cron job on Debian 13 silently stopped running 3 days ago. No new backups were being created in `/var/backups/daily/`, and no error logs or emails were generated.

## Root Causes Identified
1. **Misconfigured Crontab:** The root crontab was pointing to a non-existent or outdated script (`old_backup.sh` instead of `backup.sh`), and standard errors were silenced via `> /dev/null 2>&1`.
2. **Permissions Issue:** The correct backup script (`/opt/backup/backup.sh`) was missing executable permissions.
3. **Stale Lock File:** A previous failed run left a lock file in place, causing manual and automated runs to fail with the error: `Error: Backup already running (lock file exists)`.

## Production-Grade Solution

### 1. Fix Permissions and Clear Stale Locks
```bash
# Grant executable permissions to the correct backup script
sudo chmod +x /opt/backup/backup.sh

# Remove the stale lock file blocking execution
sudo rm -f /var/run/backup.lock /tmp/backup.lock /opt/backup/backup.lock
```

### 2. Correct the Crontab Definition
Run `sudo crontab -e` and update the execution target to the correct script path:

**Before:**
```text
*/5 * * * * /opt/backup/old_backup.sh > /dev/null 2>&1
```

**After:**
```text
*/5 * * * * /opt/backup/backup.sh > /dev/null 2>&1
```

### 3. Verification & Submission
```bash
# Manually trigger the backup to immediately satisfy the 10-minute validity test
sudo /opt/backup/backup.sh

# Verify the backup file was successfully created
ls -lh /var/backups/daily/

# Submit the challenge solution
/home/admin/agent/check.sh
```
