# Module 11: Cron & Scheduling

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you schedule tasks through:

```
Windows:
  Task Scheduler (taskschd.msc) → GUI for scheduled tasks
  Get-ScheduledTask → List all tasks
  Get-ScheduledTaskInfo → Task info (next run, last run)
  Register-ScheduledTask → Create new task
  Start-ScheduledTask → Run task now
  Disable-ScheduledTask / Enable-ScheduledTask
  schtasks /create /tn "MyTask" /tr "cmd.exe" /sc daily /st 02:00 → CLI create
  schtasks /run /tn "MyTask" → Run now
  schtasks /delete /tn "MyTask" → Delete
  schtasks /query /v /fo list → List all with verbose info
 schtasks /create /tn "Backup" /tr "C:\backup.bat" /sc daily /st 02:00 /ru SYSTEM
  schtasks /create /tn "Cleanup" /tr "C:\cleanup.ps1" /sc weekly /d MON /st 03:00
```

Windows scheduling is **Task Scheduler-driven**, configured via GUI or `schtasks`/`Register-ScheduledTask`. Tasks run as **services** or **user sessions**, with **SYSTEM**, **LocalService**, or **NetworkService** account options. **Triggers** include time-based (daily, weekly, monthly), event-based (on login, on boot), and idle conditions.

## The Shift

Linux scheduling is **CLI-and-file-driven** — no Task Scheduler GUI. Crontab files replace the GUI, and scheduling is **text-based**: `0 2 * * *` means "2 AM daily". Unlike Windows Task Scheduler which supports **event triggers** (on login, on boot, on error), Linux cron is **time-only** — event-based triggers belong to other systems (inotify for file events, systemd path timers for boot conditions). **Linux cron is simpler** — no event triggers, no conditions — but **more powerful** with per-user crontabs and root crontab for system-wide scheduling. **Windows Task Scheduler** is a full job engine; **cron** is a time-based scheduler.

---

## Crontab Basics

### User Crontab

```bash
# Edit crontab (Windows: Register-ScheduledTask)
crontab -e                          # Edit your crontab
crontab -l                          # List your crontab (Windows: Get-ScheduledTask)
crontab -r                          # Remove your crontab (Windows: Unregister-ScheduledTask)
crontab -e -u <username>            # Edit another user's crontab (root only)

# Where crontab is stored
/var/spool/cron/crontabs/<username>  # Debian/Ubuntu crontab file
/var/spool/cron/<username>           # RHEL/CentOS crontab file

# Crontab format (Windows: schtasks /sc daily/weekly/monthly/time)
# ┌────── minute (0-59)
# │ ┌────── hour (0-23)
# │ │ ┌────── day of month (1-31)
# │ │ │ ┌────── month (1-12)
# │ │ │ │ ┌────── day of week (0-7, both 0 and 7 = Sunday)
# │ │ │ │ │
# * * * * * command

# Common examples (Windows equivalent)
0 2 * * * /usr/local/bin/backup.sh      # Daily at 2 AM (Windows: /sc daily /st 02:00)
*/5 * * * * /usr/local/bin/check.sh     # Every 5 minutes (Windows: /sc minute /mo 5)
0 9 * * 1 /usr/local/bin/monday.sh      # Monday at 9 AM (Windows: /sc weekly /d MON)
0 0 1 * * /usr/local/bin/monthly.sh     # 1st of every month (Windows: /sc monthly)
30 3 * * 0 /usr/local/bin/sunday.sh     # Sunday at 3:30 AM (Windows: /sc weekly /d SUN)
*/10 * * * * /usr/local/bin/health.sh   # Every 10 minutes (Windows: /sc minute /mo 10)
0 8-17 * * 1-5 /usr/local/bin/work.sh   # Every hour during work hours M-F (Windows: /sc daily /st 08:00 /ri 3600 /du 09:00 /sd MON /ed FRI)
```

### Cron Special Strings

```bash
# Cron special time strings (Windows: schtasks /sc with specific options)
@reboot /usr/local/bin/startup.sh        # At boot (Windows: /sc onstart)
@yearly /usr/local/bin/yearly.sh         # Once a year (Windows: /sc monthly /mo 1 /st 00:00)
@monthly /usr/local/bin/monthly.sh       # Once a month
@weekly /usr/local/bin/weekly.sh         # Once a week
@daily /usr/local/bin/daily.sh           # Once a day (Windows: /sc daily /st 00:00)
@hourly /usr/local/bin/hourly.sh         # Once an hour
```

### Root Crontab (System Crontab)

```bash
# Root crontab (Windows: System-level scheduled tasks)
crontab -e -u root                       # Edit root crontab
sudo crontab -e                          # Edit root crontab (alternate)
sudo crontab -l                          # List root crontab

# System-wide crontab (Windows: Register-ScheduledTask -RunLevel Highest)
/etc/crontab                             # System crontab (has username field)
cat /etc/crontab
# SHELL=/bin/sh
# PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
# m h dom mon dow user  command
17 * * * * root cd / && run-parts --report /etc/cron.hourly
25 6 * * * root test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
```

### Cron Directories

```bash
# Cron directories (Windows: Task Scheduler task definitions in C:\Windows\System32\Tasks)
/etc/cron.d/                             # System cron files
/etc/cron.daily/                         # Scripts run daily by anacron
/etc/cron.hourly/                        # Scripts run hourly by anacron
/etc/cron.weekly/                        # Scripts run weekly
/etc/cron.monthly/                       # Scripts run monthly
ls -la /etc/cron.d/                      # List system cron files
```

### Environment Variables

```bash
# Cron environment (Windows: Task Scheduler works in SYSTEM context)
# Cron has minimal environment — always set PATH!
MAILTO=admin@example.com                 # Mail results to this address
SHELL=/bin/bash                          # Set shell
PATH=/usr/local/bin:/usr/bin:/bin        # Set PATH
# Cron ignores your interactive shell environment — no ~/.bashrc, no aliases
# Always use full paths in cron commands!
```

---

## Anacron — For Non-24/7 Systems

```bash
# Anacron (Windows: no direct equivalent — Task Scheduler handles this)
# Anacron runs jobs even if the system was off at scheduled time
# Useful for laptops/desktops (Windows: Task Scheduler "Run if running" settings)

sudo apt install anacron                   # Install anacron
cat /etc/anacrontab                        # Anacron config
# 1  5  cron.daily        # Run daily jobs with 5 min delay
# 7  10 cron.weekly       # Run weekly jobs with 10 min delay
# 30 15 cron.monthly      # Run monthly jobs with 15 min delay
```

---

## Systemd Timers — Modern Alternative to Cron

```bash
# Systemd timers (Windows: no direct equivalent — closest is Task Scheduler with on-boot triggers)
# Systemd timers are the modern way to schedule jobs — replace cron for systemd-managed services

# Create a timer unit (Windows: Register-ScheduledTask -Trigger Boot)
sudo nano /etc/systemd/system/backup.timer
# [Unit]
# Description=Daily backup timer

# [Timer]
# OnCalendar=*-*-* 02:00:00    # Daily at 2 AM (same as cron)
# Persistent=true                 # Run missed jobs on next boot
# RandomizedDelaySec=60          # Add 60s random delay (spread load)

# [Install]
# WantedBy=timers.target

# Create the corresponding service unit
sudo nano /etc/systemd/system/backup.service
# [Unit]
# Description=Run backup

# [Service]
# Type=oneshot
# ExecStart=/usr/local/bin/backup.sh
```

### Timer Management

```bash
# Timer management (Windows: Start-ScheduledTask, Get-ScheduledTaskInfo)
systemctl start backup.timer       # Start timer
systemctl stop backup.timer        # Stop timer
systemctl status backup.timer      # Timer status
systemctl list-timers --all        # All timers (Windows: Get-ScheduledTask | Where-Object State -eq 'Ready')
systemctl enable backup.timer      # Start on boot
systemctl disable backup.timer     # Disable on boot
systemctl daemon-reload            # Reload timer config

# List all timers (Windows: Get-ScheduledTask)
systemctl list-timers              # Show all active timers
systemctl list-timers --all        # Include inactive timers

# Timer state (Windows: Get-ScheduledTaskInfo)
systemctl show backup.timer        # Full timer properties
```

---

## One-Shot Commands

```bash
# At command (Windows: schtasks /run /tn ...)
at now + 5 minutes /cmd "echo 'Hello'"  # Run in 5 minutes (deprecated in Ubuntu)
at 14:30 /cmd "echo 'Hello'"            # Run at specific time

# Noatime — schedule a one-time command (Windows: schtasks /create /tn "Once" /tr "cmd.exe" /sc once /st 14:30)
at 14:30 /interactive "bash -c 'echo done'"  # One-time with output
```

---

## Hands-On Exercise

```bash
# 1. User crontab
crontab -l                          # List current crontab
crontab -e                          # Edit crontab (add: */5 * * * * /usr/local/bin/check.sh)
crontab -l                          # Verify
crontab -r                          # Remove crontab (careful!)

# 2. System crontab
sudo crontab -e                     # Edit root crontab
sudo crontab -l                     # Verify

# 3. System cron directories
ls -la /etc/cron.d/                 # System cron files
ls -la /etc/cron.daily/             # Daily scripts
ls -la /etc/cron.hourly/            # Hourly scripts

# 4. Systemd timers
systemctl list-timers --all         # All timers
systemctl status systemd-timer      # Timer service status

# 5. Create a test systemd timer
sudo nano /etc/systemd/system/test.timer
# [Unit]
# Description=Test timer

# [Timer]
# OnBootSec=5min
# OnUnitActiveSec=15min
# Persistent=true

# [Install]
# WantedBy=timers.target

sudo nano /etc/systemd/system/test.service
# [Unit]
# Description=Test service

# [Service]
# Type=oneshot
# ExecStart=/bin/echo "Timer fired"

sudo systemctl daemon-reload
sudo systemctl enable --now test.timer
systemctl list-timers | grep test   # Verify timer
```

---

## Mental Model Shift

| Windows Scheduler Mindset | Linux Scheduler Mindset |
|--|--|
| Task Scheduler GUI (taskschd.msc) | `crontab -e` (text file) |
| Get-ScheduledTask | `crontab -l` |
| Register-ScheduledTask | `crontab -e` |
| Unregister-ScheduledTask | `crontab -r` |
| Start-ScheduledTask | `systemctl start <timer>` or run script directly |
| schtasks /create /sc daily /st 02:00 | `0 2 * * * command` |
| schtasks /sc weekly /d MON | `0 0 * * 1 command` |
| schtasks /sc monthly /mo 1 | `0 0 1 * * command` |
| schtasks /sc minute /mo 5 | `*/5 * * * * command` |
| schtasks /sc onstart | `@reboot command` or systemd timer `OnBootSec=` |
| schtasks /sc onlogon | No direct cron equivalent — use systemd path timer or startup script |
| schtasks /sc onidle | No direct cron equivalent — use systemd path timer or autostart |
| Task triggers (time, event, idle) | cron: time only, systemd: time + events |
| Run whether user is logged on | cron runs in user context (always runs) |
| Run with highest privileges | sudo crontab -e |
| Run as SYSTEM account | `/etc/crontab` or root crontab |
| Run as user account | `crontab -u <user> -e` |
| Task conditions (network, battery, idle) | No cron equivalent — use systemd path/user timers |
| Task history in Event Viewer | Mail to MAILTO or check /var/log/cron |
| Task output captured | Email to MAILTO or redirect to log file |
| schtasks /run /tn "MyTask" | Run the script directly: `/path/to/script.sh` |
| Task scheduler log (Microsoft-Windows-TaskScheduler/Operational) | `/var/log/syslog` or `mail` log (cron output) |
| Register-ScheduledTask -Trigger "Boot" | `@reboot command` or systemd timer `OnBootSec=` |
| schtasks /create /sc once /st 14:30 | `at 14:30` (deprecated) or `cron` with single-date entry |

**Key takeaway:** Linux scheduling is **text-driven** — use `crontab -e` for user jobs and `/etc/crontab` or `/etc/cron.d/` for system jobs. Cron syntax (`0 2 * * *`) is **more compact** than Windows `schtasks` but **only supports time triggers** — no event-based triggers like Windows Task Scheduler. For **event-based triggers** (on file change, on boot conditions), use **systemd timers** (`OnBootSec=`, `OnCalendar=`). **Always use full paths** in cron (no `$PATH` inheritance like PowerShell). **Cron runs silently** — output goes to email (set `MAILTO`) or must be redirected to a log file. **Systemd timers** (modern approach) are the closest to Windows Task Scheduler with their `systemctl list-timers` (like `Get-ScheduledTask`), `Persistent=true` (like "Run if missed"), and `OnBootSec=` (like "On start" triggers). **Anacron** handles missed jobs on non-24/7 systems (laptops/desktops). **No GUI** for scheduling — everything is CLI/text.
