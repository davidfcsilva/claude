# Linux for Windows Administrators

A structured curriculum designed to help Windows Administrators and Engineers transition to Linux.

Each module is designed to fit in a **30-minute learning window** and includes side-by-side comparisons with Windows equivalents.

## Prerequisites

- A Windows Admin who understands: Active Directory, Group Policy, PowerShell, Windows Services, Event Viewer, Task Scheduler, NTFS permissions, IIS, and basic networking via `ipconfig`/`Get-Net*` cmdlets.
- A Linux VM (Ubuntu Server 22.04+ recommended) or WSL2 instance.

## Course Structure

| Module | Topic | Windows Equivalent |
|--------|-------|-------------------|
| 01 | Boot Process | NTLDR → winload → SMSS → Wininit |
| 02 | Filesystem Hierarchy | Drive letters, C:\Windows, C:\Program Files |
| 03 | Shell & Bash Basics | PowerShell, CMD |
| 04 | File Permissions | NTFS ACLs, Share permissions |
| 05 | User & Group Management | Active Directory, Local Users |
| 06 | Package Management | winget, WSUS, MSI installers |
| 07 | Systemd & Services | Windows Services (sc.exe, net start) |
| 08 | Process Management | Task Manager, Get-Process |
| 09 | Networking | ipconfig, Get-Net*, Routing |
| 10 | Logging & Diagnostics | Event Viewer, Wevtutil |
| 11 | Cron & Scheduling | Task Scheduler, Scheduled Tasks |
| 12 | Disk & Storage | Disk Management, Storage Explorer |
| 13 | Firewall & Security | Windows Defender Firewall, netsh advfirewall |
| 14 | Remote Access & SSH | RDP, WinRM, PsExec |
| 15 | System Monitoring | Performance Monitor, perfmon, counters |
| 16 | Scripting Fundamentals | PowerShell DSC, automation scripts |

## How to Use This Course

1. Work through modules sequentially — each builds on the last.
2. Follow along on a live Linux terminal. Every command shown is typed and run, not just theory.
3. Compare each concept to what you already know from Windows administration.
4. At the end of each module, review the mental model shift section to internalize the Linux mindset.

## Recommended Lab Setup

```bash
# Option A: Ubuntu VM (recommended)
# Download from ubuntu.com/server, install in Hyper-V or VirtualBox

# Option B: WSL2 (quickest start)
wsl --install -d Ubuntu-22.04
wsl --set-default-version 2
```
