# Module 8: Process Management

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage processes through:

```
Windows:
  Task Manager → Processes tab / Details tab
  tasklist → List running processes
  Get-Process → PowerShell process cmdlets
  Stop-Process, Stop-Service → Kill processes
  ps → Process tree (from Windows 10+)
  Get-Process | Sort-Object CPU → Top CPU consumers
  Get-Process -Id → Specific process info
  stop-process -Id -Force → Kill process
  Get-Process | Where-Object WorkingSet64 -gt 1GB → Memory heavy
  systeminfo → System uptime
  Get-CimInstance Win32_OperatingSystem | Select-Object LastBootUpTime
```

Windows uses **Task Manager** (GUI), **tasklist/Get-Process** (CLI), and **Get-CimInstance** (system info). Process IDs are **PIDs** and services are **Windows Services** managed via sc.exe and services.msc.

## The Shift

Linux separates **processes** from **services**. A service is just a background process started at boot via systemd. Process management in Linux is more granular — you see **threads**, **nice values**, **states**, and **hierarchical trees**. The core commands map to Windows tools, but the depth and composition differ.

---

## Viewing Processes

### List and Monitor Processes

```bash
# List processes (Windows: Get-Process, tasklist)
ps                              # Current shell's processes (BSD-style)
ps aux                          # ALL processes (System V-style, most common)
ps -ef                          # All processes (full format, equivalent to ps aux)

# Detailed process listing (Windows: Get-Process * | Sort-Object CPU -Descending)
ps aux --sort=-%cpu | head -15  # Top 15 by CPU
ps aux --sort=-%mem | head -15  # Top 15 by memory
ps aux | awk '{print $2, $3, $4, $11}' | sort -k4 -rn | head  # Sort by memory %

# Process tree (Windows: ps /tree /pid:1234)
pstree                          # Tree view of all processes
pstree -p                       # With PIDs
pstree -p <pid>                 # Tree for specific process
pstree -u                       # Show usernames

# Live monitoring (Windows: Task Manager Performance tab / Get-Process -Update)
top                             # Real-time process monitor
htop                            # Enhanced top (install: sudo apt install htop)
atop                            # Advanced system monitor (CPU, memory, disk, network)
```

### Process Fields Explained

```bash
# ps aux columns (Windows: Get-Process columns)
USER    PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
  ^^     ^^ ^^^ ^^^    ^^^   ^^^ ^^      ^^^ ^^^^   ^^^  ^^^^^
User   PID  CPU% Mem%  VSZ    RSS  TTY    State StartTime Elapsed  Command

# VSZ = Virtual Memory Size (KB)     → WorkingSet (KB)
# RSS = Resident Set Size (KB)       → WorkingSet64 (KB)
# STAT = Process State               → ExitCode + Status
# TTY = Terminal                       → ConsoleSessionId
```

### Process States

```bash
# STAT column values (Windows: Get-Process | Select-Object Status)
#   R  → Running or runnable    → Running
#   S  → Interruptible sleep    → Suspended
#   D  → Uninterruptible sleep  → Unknown
#   Z  → Zombie (dead but parent hasn't reaped) → No Windows equivalent
#   T  → Stopped (by signal)    → Stopped
#   t  → Tracing stop           → Debug
#   W  → Paging (not valid)     → —
#   X  → Dead                   → Terminated
```

---

## Finding and Killing Processes

### Find Processes

```bash
# Find by name (Windows: Get-Process -Name nginx)
ps aux | grep nginx             # Classic grep approach
pgrep nginx                     # Find PIDs by name
pgrep -a nginx                  # PIDs + command line
pgrep -f "nginx"                # Match full command line
pidof nginx                     # Get PID(s) of process

# Find by user (Windows: Get-Process -IncludeUserName | Where-Object UserName -eq "admin")
ps aux -u david                 # All processes for user david
ps -u root                      # All root processes
who                             # Logged-in users (like whoami)
w                               # Logged-in users + what they're doing

# Find by port (Windows: netstat -ano | findstr :80, Get-NetTCPConnection)
lsof -i :80                     # What process uses port 80?
ss -tlnp | grep :80             # Socket listeners on port 80
netstat -tlnp                   # All TCP listeners with PIDs

# System info (Windows: systeminfo, Get-CimInstance Win32_OperatingSystem)
uptime                          # System uptime (like systeminfo | findstr "Boot Time")
cat /proc/uptime                 # Raw uptime in seconds
uname -a                        # Kernel info (like systeminfo | findstr "OS Name" "OS Version")
```

### Killing Processes

```bash
# Kill processes (Windows: Stop-Process -Id / taskkill /PID)
kill <pid>                      # Send SIGTERM (graceful stop)
kill -9 <pid>                   # Send SIGKILL (force kill)
kill -15 <pid>                  # Same as kill (SIGTERM)

# Signal types (Windows: stop-process vs stop-process -force)
#   SIGTERM (15) → graceful shutdown, can be caught/handled
#   SIGKILL (9)  → force kill, cannot be caught (like stop-process -force)
#   SIGHUP (1)   → reload config (like restart-service)
#   SIGINT (2)   → interrupt (like Ctrl+C)

# Kill by name (Windows: Stop-Process -Name nginx -Force)
pkill nginx                     # Kill all processes matching name
pkill -f nginx                  # Kill by full command line
killall nginx                   # Kill all processes with exact name
killall -9 nginx                # Force kill all nginx processes

# Kill by user (Windows: Get-Process -IncludeUserName | Where-Object UserName -eq "david" | Stop-Process)
pkill -u david                  # Kill all processes for user david
killall -u david nginx          # Kill specific process for user
```

---

## Process Priorities (Nice Values)

```bash
# Nice values (Windows: PriorityClass in Get-Process)
# Normal range: -20 (highest) to 19 (lowest)
# Default: 0 (normal priority)
# Negative values require root (like running as SYSTEM)

# View nice values (Windows: Get-Process | Select-Object Name,PriorityClass)
ps -eo pid,ni,comm --sort=-ni  # Show processes sorted by nice value
top → Shift+N → sort by priority  # In top, sort by nice

# Change nice value (Windows: set-process -priority high)
nice -n 10 nginx                # Start nginx with low priority (nice=10)
renice 10 -p <pid>              # Change priority of running process
renice -10 -p <pid>             # Give higher priority (need root)

# Priority classes (Windows ↔ Linux)
# High         → nice -20 (most important, only root)
# AboveNormal  → nice -5 to -1 (root only)
# Normal       → nice 0 (default)
# BelowNormal  → nice 5 to 10
# Idle         → nice 15 to 19 (least important)
```

---

## Daemons and Background Services

```bash
# Daemons = Windows Services (background processes)
# In Linux, they're managed by systemd (not a separate service manager)

# View services (Windows: Get-Service, Get-Process | Where-Object { $_.MainWindowTitle -eq $null })
systemctl list-units --type=service    # Active services
systemctl list-units --all              # All services (active + inactive)
systemctl list-unit-files --type=service  # Services that auto-start at boot

# Service states (Windows: Running, Stopped, Starting)
#   active (running)    → Running
#   active (exited)     → Started and exited (one-shot service)
#   inactive (dead)     → Stopped
#   failed              → Failed to start (equivalent to Stopped but with error)
#   enabled             → Set to start at boot (like StartMode=automatic)
#   disabled            → Won't start at boot (like StartMode=manual)
```

---

## Hands-On Exercise

```bash
# 1. View current processes
ps aux --sort=-%cpu | head -10          # Top 10 CPU consumers
ps aux --sort=-%mem | head -10          # Top 10 memory consumers
ps aux | awk '{print $2, $3, $4, $11}' | sort -k4 -rn | head  # Sort by RSS

# 2. Real-time monitoring
top                                      # Press q to exit
# In top: M → sort by memory, P → sort by CPU
#          shift+N → sort by nice value

# 3. Find processes
pgrep -a sshd                            # Find sshd process
pidof nginx                              # Find nginx PID
lsof -i :22                              # What uses port 22?
ps aux | grep ssh                        # Find SSH-related processes

# 4. Process tree
pstree -p | head -30                     # View process tree
pstree -p <pid>                          # Tree for specific process

# 5. Process priorities
ps -eo pid,ni,comm --sort=-ni | head     # View nice values
sudo nice -n 10 top                      # Start with low priority
renice 10 -p <pid>                       # Change priority

# 6. System info
uptime                                   # How long system has been running
cat /proc/uptime                         # Raw uptime in seconds
uname -a                                 # Kernel version and info

# 7. Kill process (on a test process!)
sleep 3600 &                             # Create test process
TESTPID=$!                               # Get its PID
sleep $TESTPID                           # Kill it (use with caution!)
```

---

## Mental Model Shift

| Windows Process Mindset | Linux Process Mindset |
|--|--|
| Task Manager Processes tab | `ps aux` + `top`/`htop` |
| tasklist | `ps aux` or `pgrep` |
| Get-Process | `ps aux --sort=-%cpu` |
| Stop-Process -Id -Force | `kill -9 <pid>` or `killall -9 name` |
| Stop-Service nginx | `systemctl stop nginx` (service, not process) |
| netstat -ano \| findstr :80 | `ss -tlnp \| grep :80` or `lsof -i :80` |
| ps /tree | `pstree -p` |
| PriorityClass (6 levels) | Nice values (-20 to 19, continuous range) |
| Task Scheduler | crontab (separate module) |
| Get-CimInstance Win32_OperatingSystem | `uname -a` + `uptime` + `cat /proc/uptime` |
| Services are managed separately | Services = systemd-managed processes (one unified system) |
| System up time in Control Panel | `uptime` or `cat /proc/uptime` |
| Zombie processes don't exist in Task Manager | Zombie processes shown in `ps` (Z state) |
| One manager (Task Manager) | Many tools: `ps`, `pgrep`, `pidof`, `kill`, `pkill`, `killall`, `top`, `htop`, `atop`, `pstree` |

**Key takeaway:** Linux separates process management (`ps`, `top`, `kill`) from service management (`systemctl`). Use `ps aux --sort=-%cpu` to find CPU-heavy processes (like `Get-Process | Sort-Object CPU`), `pgrep`/`pidof` to find PIDs (like `Get-Process -Name`), and `kill`/`pkill`/`killall` to stop them (like `Stop-Process`). Linux processes have **states** (R/S/D/Z/T) shown in `ps`, **nice values** (-20 to 19) for priority (like Windows PriorityClass but continuous), and **signals** (SIGTERM=graceful, SIGKILL=force). `top`/`htop` provide real-time monitoring (like Task Manager). **Zombie processes** (Z state) are a Linux-specific concept — dead processes waiting for their parent to reap them. Always prefer `kill` (SIGTERM, default) over `kill -9` (SIGKILL) unless the process is unresponsive.
