# Module 2: Linux Filesystem Hierarchy

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, your mental model of the filesystem looks like this:

```
C:\
├── Windows\
├── Program Files\
├── Program Files (x86)\
├── Users\
├── ProgramData\
├── Temp\
└── pagefile.sys
```

Windows uses **drive letters** (C:, D:, E:) and **paths** (C:\Windows\System32) to locate files. There is one top-level namespace per drive.

## The Shift

Linux uses **a single tree** rooted at `/` with **mount points**. Every drive, USB, network share, and partition plugs into this one tree. No drive letters — just paths.

```
/                         # Root of everything (like C:\, but for ALL storage)
├── bin/                  # Essential commands (ls, cp, mkdir)
├── boot/                 # Bootloader files (kernel, GRUB)
├── dev/                  # Device files (/dev/sda, /dev/sda1)
├── etc/                  # Configuration files (like HKLM\SOFTWARE but text files)
├── home/                 # User home dirs (/home/david)
├── lib/                  # Shared libraries
├── opt/                  # Optional app packages
├── proc/                 # Process + kernel info (pseudo-FS)
├── run/                  # Runtime data (PID files, sockets)
├── sbin/                 # Essential system binaries (sudo, iptables)
├── srv/                  # System data (web roots, FTP)
├── tmp/                  # Temporary files
├── usr/                  # User programs (like C:\Program Files)
│   ├── bin/              # User commands
│   ├── lib/              # Libraries
│   ├── share/            # Read-only data
│   └── local/            # Locally installed (like C:\Program Files)
└── var/                  # Variable data (logs, caches, mail)
    ├── log/              # /var/log ← your Event Viewer
    ├── cache/            # Application caches
    └── spool/            # Print/email queues
```

### Side-by-Side: Common Paths

| Windows | Linux | What's Inside |
|---------|-------|---------------|
| `C:\Windows` | `/usr` or `/etc` | System programs + config |
| `C:\Windows\System32` | `/usr/bin`, `/usr/sbin` | Core binaries |
| `C:\Program Files` | `/usr/local` | Locally installed apps |
| `C:\ProgramData` | `/etc` and `/var` | Shared config + state |
| `C:\Users\david` | `/home/david` | User home directory |
| `C:\Users\All Users` | `/var/lib` | Per-user shared state |
| `C:\Temp` | `/tmp` | Temporary files |
| `C:\Program Files\Common Files` | `/usr/share` | Shared data files |
| `HKEY_LOCAL_MACHINE` | `/etc` + `/usr` | Registry → text files |
| `C:\Windows\Inf` | `/usr/share/doc` | Installation info |

### FHS = Your File System Layout Standard

Linux follows the **Filesystem Hierarchy Standard (FHS)**. Windows has no official standard — C:\Windows and C:\Program Files are conventions, not standards.

```bash
# See what's mounted where (Windows: Get-PSDrive -PSProvider FileSystem)
df -h

# Show mount points explicitly (Windows: Get-Volume)
mount | column -t

# FHS compliance — every distro follows this
ls -d /bin /sbin /usr /var /etc /home /tmp
```

### Drive Letters Don't Exist

This is the first mental shift. There are **no drive letters**.

```bash
# Windows: D:\, E:\, F:\ ... every drive gets a letter
# Linux: everything mounts under /

# See all block devices (Windows: Get-Disk)
lsblk

# Example output:
# NAME   MOUNTPOINT         FSTYPE  SIZE
# sda
# └─sda1 /                    ext4     50G
# └─sda2 [SWAP]               swap      8G
# sdb                               ext4    500G    # USB drive mounted under /mnt
# └─sdb1 /mnt/usb

# Manually mount a drive (Windows: New-PSDrive or diskmgmt.msc)
sudo mount /dev/sdb1 /mnt/usb    # plug it in
sudo umount /mnt/usb              # unmount it

# Mount a network share (Windows: New-PSDrive -Persist ...)
sudo mount -t cifs //fileserver/share /mnt/smb -o credentials=/etc/samba/creds
```

### /etc = Your Registry

The single most important directory for a Linux admin: **everything is text, everything is readable**.

```bash
# Network config (Windows: Get-NetIPConfiguration)
cat /etc/netplan/00-installer-config.yaml    # Ubuntu
cat /etc/NetworkManager/NetworkManager.conf   # RHEL/CentOS

# SSH config (Windows: no direct equivalent)
cat /etc/ssh/sshd_config

# DNS (Windows: Get-DnsClientServerAddress)
cat /etc/resolv.conf

# Hosts (Windows: C:\Windows\System32\drivers\etc\hosts)
cat /etc/hosts

# Fstab — what partitions mount where (Windows: diskpart + registry)
cat /etc/fstab

# Example output:
# /dev/sda2  /         ext4  defaults  0 1
# /dev/sda1  /boot     ext4  defaults  0 2
# /dev/sda3  none      swap  sw        0 0
```

### /var/log = Your Event Viewer

Linux logs are text files. Any log viewer works.

```bash
# All log files (Windows: Event Viewer → Linux → /var/log)
ls /var/log/

# Core system log (Windows: Event Viewer → System)
cat /var/log/syslog          # Debian/Ubuntu
cat /var/log/messages        # RHEL/CentOS

# Auth log (Windows: Event Viewer → Security)
cat /var/log/auth.log        # Debian/Ubuntu
cat /var/log/secure          # RHEL/CentOS

# Follow a log in real time (Windows: wevtutil subscribe ...)
tail -f /var/log/syslog

# Filter a log for errors (Windows: Get-EventLog System -EntryType Error)
grep -i error /var/log/syslog | tail -20
```

### /tmp — Temporary Files

```bash
# Where temp files live (Windows: $env:TEMP, C:\Windows\Temp)
echo $TMPDIR                  # user-specific temp
ls -lh /tmp                   # system-wide temp
df -h /tmp                    # check /tmp size (sometimes tmpfs)

# Clean up (Windows: Clean-RecycleBin / disk cleanup)
find /tmp -type f -atime +7 -delete    # files not accessed in 7 days
```

### /dev — Device Files

```bash
# All block devices (Windows: Get-PhysicalDisk)
lsblk

# All character devices (Windows: Get-WmiObject Win32_PnPEntity)
ls /dev/tty* /dev/null /dev/zero

# Disk I/O stats (Windows: Get-Counter '\\PhysicalDisk(*)\\*')
iostat -x 1

# Read raw disk (like disk management — use with caution!)
sudo fdisk -l
```

## Hands-On Exercise

```bash
# 1. Map your filesystem
df -h                          # What's mounted where?
du -sh /* 2>/dev/null          # How big is each top-level dir?

# 2. Find where your home directory sits
df -h $HOME

# 3. Check config files (your "registry")
cat /etc/fstab
cat /etc/hosts
cat /etc/resolv.conf

# 4. Check logs (your "Event Viewer")
ls /var/log/
journalctl --no-pager -n 20    # last 20 log lines

# 5. See what's mounted
mount | column -t
lsblk

# 6. Find a large directory (like Disk Usage Analyzer)
du -sh /usr/* | sort -rh | head -10
```

## Mental Model Shift

| Windows Mindset | Linux Mindset |
|-----------------|---------------|
| C:\, D:\, E:\ — each drive is separate | `/` — one tree, everything mounts under it |
| Drive letters can conflict (USB takes F:\) | Mount under any directory — no letter conflicts |
| `C:\Windows` is a convention | `/etc`, `/var`, `/usr` are standards (FHS) |
| Registry = binary database | `/etc` = plain text files, readable by anyone |
| Event Viewer = GUI for event logs | `/var/log` = text files, use grep/tail/journalctl |
| `C:\Program Files` for apps | `/usr` for distro apps, `/usr/local` for manual installs |
| `Get-PSDrive` for network drives | `mount` + `/etc/fstab` for permanent mounts |
| Disk Management GUI | `fdisk`, `lsblk`, `mount` from CLI |
| Configuration in registry or .ini/.xml scattered | Everything in `/etc`, organized by service name |

**Key takeaway:** Linux has one filesystem tree. There are no drive letters. Everything is a file, everything is under `/`. The FHS standard means if you know `/etc`, you know where the config is on any Linux system — no guessing, no registry dives, no GUI hunts.
