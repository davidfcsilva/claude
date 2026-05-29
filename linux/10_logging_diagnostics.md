# Module 10: Logging & Diagnostics

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage logging through:

```
Windows:
  Event Viewer (eventvwr.msc) → GUI for system/app logs
  Get-EventLog → Legacy event log access
  Get-WinEvent → Modern event log access
  wevtutil → Event log CLI
  Get-Content C:\Windows\System32\winevt\Logs\*.evtx → Read log files
  wevtutil qe System /c:10 → Last 10 system events
  wevtutil qe Application /c:5 → Last 5 app events
  Get-EventLog -Log System -Newest 10 → Top 10 system events
  Get-EventLog -Log System -EntryType Error → System errors only
  wevtutil epl System C:\temp\system.evtx → Export event log
  wevtutil ql System → Clear system log
```

Windows logs are in **EVTX format**, structured as **Channels** (System, Application, Security, Setup), accessed via `Get-WinEvent` (PowerShell) or `wevtutil` (CLI).

## The Shift

Linux uses a **unified logging daemon** (systemd-journald) that replaces Windows Event Log. There are no .evtx files — logs are stored in **binary journal files** accessed via `journalctl`. However, Linux also has the traditional **syslog** system (rsyslog/syslog-ng) that writes plain-text files to `/var/log/`. Linux logging is **more granular** — you see per-daemon output, kernel messages, auth logs, and cron logs separately, whereas Windows consolidates them into channels.

---

## Journalctl — The Primary Tool

### View Logs

```bash
# View logs (Windows: Get-WinEvent -LogName System -Newest 10)
journalctl                           # All logs (boot to now)
journalctl -f                        # Follow live (like tail -f, Windows: Get-WinEvent | Format-List)
journalctl --since "1 hour ago"      # Last hour
journalctl --since "2024-01-15 14:00:00" --until "2024-01-15 15:00:00"  # Time range
journalctl -u nginx                  # Logs for a specific service (Windows: Get-WinEvent -FilterHashtable {LogName='Application'; Id=1234})
journalctl -u ssh --since today      # SSH logs from today

# Filter by boot (Windows: no direct equivalent — filter by time)
journalctl -b                        # Current boot
journalctl -b -1                     # Previous boot
journalctl -b -2                     # Two boots ago
journalctl --list-boots              # List all boots (Windows: Get-WinEvent -LogName "Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational")

# Level filtering (Windows: Get-WinEvent -FilterHashtable {Level=2} for Error)
#   emerg (0) → Critical
#   alert (1)
#   crit (2)
#   err (3)  → Error
#   warning (4) → Warning
#   notice (5)
#   info (6)  → Information
#   debug (7)  → Verbose/Debug
journalctl -p err                    # Errors and above
journalctl -p warning                # Warnings and above
journalctl -p emerg                  # Emergencies only

# Field filtering (Windows: Get-WinEvent | Where-Object Level -eq 2)
journalctl _PID=1234                 # Filter by PID
journalctl _COMM=nginx               # Filter by command
journalctl _UID=0                    # Filter by UID
journalctl SYSLOG_FACILITY=daemon    # Filter by facility
```

### Journalctl Output Formats

```bash
# Output formats (Windows: Get-WinEvent -Property *)
journalctl -o short                  # Normal (default, compact)
journalctl -o verbose                # All metadata fields
journalctl -o json                   # JSON output (like PowerShell ConvertTo-Json)
journalctl -o json | jq .            # Pretty-print JSON (install jq: sudo apt install jq)
journalctl -o short-iso              # ISO timestamps
journalctl -o cat                    # Raw message only (no metadata)

# Show log entries with their full context
journalctl --no-pager                # Without pager (like | more)
journalctl -n 50                     # Last 50 entries (Windows: Get-WinEvent -MaxEvents 50)
journalctl -n -50                    # Same as above
```

---

## Traditional Log Files (syslog)

```bash
# Log file locations (Windows: C:\Windows\System32\winevt\Logs\*.evtx)
/var/log/syslog                      # Main log (Ubuntu/Debian)
/var/log/messages                    # Main log (RHEL/CentOS)
/var/log/auth.log                    # Authentication (Windows: Security.evtx)
/var/log/secure                      # Authentication (RHEL/CentOS)
/var/log/kern.log                    # Kernel messages (Windows: System.evtx)
/var/log/dmesg                       # Kernel ring buffer (like dmesg.exe)
/var/log/cron.log                    # Cron jobs (Windows: TaskScheduler.evtx)
/var/log/faillog                     # Failed logins (Windows: Security.evtx - login failures)
/var/log/wtmp                        # Login records (Windows: wevtutil qe Security /q"[System[Provider[@Name='Microsoft-Windows-Security-Auditing']]]")
/var/log/btmp                        # Failed login attempts
/var/log/lastlog                     # Last login per user
/var/log/mail.log                    # Mail server (Windows: Application log for mail server)
/var/log/nginx/error.log             # Nginx error (Windows: Application log for IIS)
/var/log/nginx/access.log            # Nginx access (like IIS logs in %SystemDrive%\inetpub\logs\LogFiles\)
/var/log/apache2/error.log           # Apache error
/var/log/apache2/access.log          # Apache access
/var/log/daemon.log                  # Daemon messages
/var/log/mail.info                   # Mail info
/var/log/mail.warn                   # Mail warnings
/var/log/mail.err                    # Mail errors

# View log files (Windows: Get-Content C:\Windows\System32\winevt\Logs\System.evtx)
cat /var/log/syslog                  # Read entire file
tail -f /var/log/syslog              # Live follow
tail -100 /var/log/syslog            # Last 100 lines
grep "error" /var/log/syslog         # Search for errors
grep -i "failed" /var/log/auth.log   # Search for failed logins
zcat /var/log/syslog.1.gz            # Previous day's log
zgrep "error" /var/log/syslog.1.gz   # Search in compressed log
ls -la /var/log/                     # List all logs
```

### Log Rotation

```bash
# Log rotation (Windows: Event log "When full" settings — don't overwrite / archive)
ls /var/log/ | grep -E '\.(1|gz)$'   # Rotated log files
logrotate --version                    # Check logrotate version
cat /etc/logrotate.conf                # Global logrotate config
cat /etc/logrotate.d/syslog            # Per-service rotation
```

---

## System Information & Diagnostics

### Kernel & Boot Logs

```bash
# Kernel messages (Windows: Get-WinEvent -LogName System | Where-Object Id -eq 12)
dmesg                                # Kernel ring buffer
dmesg | grep -i error                # Kernel errors
dmesg --time-iso                       # ISO timestamps
dmesg -T                             # Human-readable timestamps
dmesg --level=err,crit,alert,emerg    # Error level only
dmesg -w                               # Follow mode (like journalctl -f)
```

### Boot Diagnostics

```bash
# Boot logs (Windows: Get-WinEvent -LogName Setup / LogName System | Where-Object Id -eq 6005)
journalctl -b                         # Boot messages
last reboot                           # Reboot history
last log                              # Login history
lastb                               # Failed login history
who / w                             # Who's logged in
last -n 20                          # Last 20 logins
```

### System Health

```bash
# System health (Windows: Get-Counter, Get-NetTCPConnection, Get-Process)
dmesg                                # Kernel health
uptime                               # System uptime
cat /proc/loadavg                    # CPU load averages
cat /proc/meminfo                    # Memory info (Windows: Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory)
free -h                              # Memory usage (human-readable)
df -h                                # Disk usage (Windows: Get-CimInstance Win32_LogicalDisk)
cat /proc/cpuinfo                    # CPU info (Windows: Get-CimInstance Win32_Processor)
lscpu                                # CPU summary
lshw -short                          # Hardware summary
lsblk                                # Block devices
lspci | grep -i -A4 -B4 -C1           # PCI devices
lsusb                                # USB devices
```

### Disk I/O Diagnostics

```bash
# Disk I/O (Windows: Get-Counter "\PhysicalDisk(*)\*", Get-Counter "\LogicalDisk(*)\*")
iostat                               # Disk I/O stats (install: sudo apt install sysstat)
iotop                                # Real-time disk I/O (install: sudo apt install iotop)
df -h                                # Disk usage
du -sh /var/log/*                    # Log file sizes
lsblk                                # Block devices
```

### Network Diagnostics

```bash
# Network diagnostics (Windows: Get-NetTCPConnection, Get-NetAdapterStatistics, Test-NetConnection)
ss -s                                # Socket stats
netstat -anp                         # All connections with PIDs
cat /proc/net/dev                    # Interface traffic stats
ethtool eth0                         # Interface details
ping -c 4 google.com                 # Connectivity
traceroute google.com                # Route trace
dig google.com                       # DNS
nslookup google.com                  # DNS
mtr google.com                       # Merged ping/traceroute
curl -I http://localhost             # HTTP headers
wget --spider http://localhost       # Test HTTP
nc -zv localhost 22                  # Port check
```

---

## Hands-On Exercise

```bash
# 1. Journal logs
journalctl -n 20                     # Last 20 entries
journalctl -u nginx                  # Nginx logs
journalctl -p err                    # Errors only
journalctl --since "1 hour ago"      # Last hour
journalctl -f                        # Follow mode
journalctl -b                        # Current boot
journalctl -b -1                     # Previous boot
journalctl --list-boots              # Boot history

# 2. Log files
tail -f /var/log/syslog              # Live syslog
grep -i "error" /var/log/syslog      # Search errors
grep -i "failed" /var/log/auth.log   # Failed logins
ls -lh /var/log/                     # Log file sizes

# 3. Kernel
dmesg | tail -20                     # Recent kernel messages
dmesg | grep -i error                # Kernel errors
dmesg --time-iso                     # ISO timestamps

# 4. Boot & login history
last reboot                          # Reboot history
last log                             # Login history
lastb                                # Failed logins
who / w                              # Current logins

# 5. System health
uptime                               # Uptime
free -h                              # Memory
df -h                                # Disk usage
cat /proc/loadavg                    # Load averages
cat /proc/cpuinfo                    # CPU info
lscpu                                # CPU summary
uname -a                             # Kernel version
cat /etc/os-release                  # OS version
```

---

## Mental Model Shift

| Windows Log Mindset | Linux Log Mindset |
|--|--|
| Event Viewer (GUI) | `journalctl` (CLI) |
| Get-WinEvent -LogName System | `journalctl -b` or `journalctl -u <service>` |
| Get-WinEvent -FilterHashtable {Level=2} | `journalctl -p err` |
| Get-WinEvent -LogName Security | `journalctl -u ssh` + `/var/log/auth.log` |
| Wevtutil epl System C:\temp\log.evtx | `journalctl --output=json > /tmp/log.json` |
| Wevtutil ql System | `journalctl --vacuum-time=1d` |
| Get-WinEvent | Format-List | `journalctl -o verbose` |
| Get-WinEvent | ConvertTo-Json | `journalctl -o json \| jq .` |
| Event log channels (System, Application, Security, Setup) | Services + `/var/log/` files |
| Security.evtx | `/var/log/auth.log` |
| Application.evtx | `/var/log/syslog` or `/var/log/<service>/` |
| System.evtx | `/var/log/kern.log` + `dmesg` |
| Setup.evtx | `journalctl -b` |
| Get-EventLog -Log System -EntryType Error | `journalctl -p err` or `grep "error" /var/log/syslog` |
| Get-EventLog -Log System -Newest 10 | `journalctl -n 10` |
| Log file rotation (Event Viewer settings) | `logrotate` (automatic, via `/etc/logrotate.conf`) |
| Log files are .evtx (binary) | Logs are plain text + binary journal |
| Event IDs (4624 = login, 4625 = failed login) | Log patterns: "Accepted password" / "Failed password" |
| wevtutil qe System /c:10 | `journalctl -n 10` |
| Log files in C:\Windows\System32\winevt\Logs\ | Logs in `/var/log/` |
| One system (Event Viewer) for all logs | Separate logs per service + journal for everything |
| Get-Content on .evtx | `grep` / `zgrep` on `/var/log/` |
| PerfMon counters | `iostat`, `free`, `cat /proc/*/loadavg` |
| Task Manager for process monitoring | `top` / `htop` / `atop` |

**Key takeaway:** Linux has **two logging systems**: `journalctl` (systemd journal, modern unified log) and `/var/log/` (traditional syslog files). Use `journalctl` as your primary tool — it replaces Event Viewer + Get-WinEvent + wevtutil combined. `journalctl -u <service>` finds service logs (like `Get-WinEvent -LogName Application | Where-Object Id -eq 1234`), `journalctl -p err` filters by severity, `journalctl -f` follows live, and `journalctl -b/-b-1` navigates boots. **Traditional log files** (`/var/log/syslog`, `/var/log/auth.log`, etc.) are plain text — use `grep`, `tail`, `zcat` on them. Linux logs are **per-service** rather than per-channel: each daemon writes to its own file or journal unit. **Log rotation is automatic** via `logrotate` (Windows: Event Viewer "When full" settings). `dmesg` replaces kernel log viewing (`Get-WinEvent -LogName System | Where-Object Id -eq 12`). **Authentication logs** go to `/var/log/auth.log` (Ubuntu) or `/var/log/secure` (RHEL) — equivalent to Windows Security.evtx. **No Event Viewer GUI** — everything is CLI-driven.
