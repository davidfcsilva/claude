# Module 1: The Linux Boot Process

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you understand the boot flow:

```
UEFI/BIOS → Boot Manager (BCD) → winload.exe → NT Kernel + Registry
         → SMSS (Session Manager) → services.exe + lsass.exe → Logon Screen
```

Key tools: `bcdedit`, `bootrec`, `Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager`, Event Viewer → Boot events.

## prostit

Linux boot achieves the same result through text files instead of binary stores:

```
UEFI/BIOS → Bootloader (GRUB) → Linux Kernel + initramfs → systemd (PID 1)
         → Targets activate → Services start → Login prompt
```

### Step-by-Step Comparison

| Step | Windows | Linux | What Happens |
|------|---|---|-- |
| 1 | UEFI/BIOS firmware | UEFI/BIOS firmware | Same. POST, hardware init |
| 2 | UEFI reads BCD store (`\EFI\Microsoft\Boot\BCD`) | UEFI reads GRUB (`/boot/grub/grub.cfg`) | Bootloader config. GRUB = Windows Boot Manager |
| 3 | `winload.exe` loads kernel + registry hives | Kernel (`/boot/vmlinuz`) + initramfs loaded | Kernel into RAM. initramfs = temporary root FS with hardware drivers |
| 4 | `SMSS.exe` → `services.exe` + `lsass.exe` | `systemd` becomes PID 1 | systemd = services.exe + session manager combined. Config is plain text, not registry |
| 5 | Services start per registry | Services start per target (multi-user, graphical) | Same concept, different format |
| 6 | Logon screen (LSASS ready) | Login prompt (console + SSH) | Authentication ready |

### Essential Commands

```bash
# View bootloader config           Windows: bcdedit
sudo grep menuentry /boot/grub/grub.cfg

# View kernel parameters           Windows: bcdedit /enum {current}
cat /proc/cmdline

# Kernel version                   Windows: (Get-CimInstance Win32_OperatingSystem).Version
uname -r

# Boot time + uptime               Windows: systeminfo | find "Boot Time"
uptime
systemctl is-system-running

# Boot log                         Windows: Event Viewer → System log
journalctl -b         # current boot
journalctl -b -1      # previous boot
```

### GRUB = Your Windows Boot Manager

| Windows Boot Manager | GRUB |
|---|---|
| `bcdedit` | Edit `/etc/default/grub`, then `sudo update-grub` |
| Safe Mode | Kernel param `single` or `systemd.unit=rescue.target` |
| Dual-boot entries | GRUB menu auto-detects multiple OS entries |
| `bootrec /fixboot` | `sudo grub-install /dev/sda` |
| `bcdedit /timeout 30` | `GRUB_TIMEOUT=10` in `/etc/default/grub` |

```bash
# Change boot timeout (Windows: bcdedit /timeoutvalues 30)
sudo vi /etc/default/grub
# Edit: GRUB_TIMEOUT=10
sudo update-grub

# Change default boot entry (Windows: bcdedit /default {identifier})
sudo vi /etc/default/grub
# GRUB_DEFAULT=0  (0=first, 1=second, or use title string)
sudo update-grub
```

### systemd = Your services.exe

systemd reads unit files (plain text) instead of registry keys.

```bash
# Service boot log (Windows: Event Viewer → Svc)
journalctl -u sshd --since "10 minutes ago"

# Boot timeline (Windows: no built-in equivalent)
systemd-analyze blame          # time per service, sorted slowest-first
systemd-analyze critical-chain # dependency tree with timings

# Example output:
#   32.412s NetworkManager-wait-online.service
#   12.001s systemd-udev-settle.service
#    5.432s sshd.service
#    1.200s systemd-journald.service
```

### Targets = Boot Modes

| Windows | Linux Target | Command |
|---|---|---|
| Normal Boot | `multi-user.target` (CLI) / `graphical.target` (GUI) | Default |
| Safe Mode | `rescue.target` | `sudo systemctl isolate rescue.target` |
| Safe Mode + Net | Manually start network in rescue | Start only what you need |
| Safe Mode + CMD | `emergency.target` | Root shell, minimal FS mounted |
| Last Known Good Config | No direct equivalent — use filesystem snapshots | Different strategy (btrfs/zfs rollback) |

### /proc — Read System State as Files

```bash
cat /proc/cpuinfo     # CPU (Windows: Get-CimInstance Win32_Processor)
cat /proc/meminfo     # RAM (Windows: Get-CimInstance Win32_PhysicalMemory)
cat /proc/diskstats   # Disk I/O (Windows: Get-Counter '\\PhysicalDisk\...')
cat /proc/version     # Kernel (Windows: winver)
ls /sys/block/        # Block devices (Windows: Get-PhysicalDisk)
```

## Hands-On Exercise

```bash
# 1. Check boot loader
ls /boot/grub/grub.cfg

# 2. Total boot time
systemd-analyze

# 3. What slowed boot down
systemd-analyze blame | head -10

# 4. Dependency tree
systemd-analyze critical-chain

# 5. Kernel ring buffer (Windows: wevtutil q-log System)
dmesg | head -20
```

## Mental Model Shift

| Windows Mindset | Linux Mindset |
|---|---|
| Boot config in binary BCD store | Boot config = text files in `/boot/grub/` and `/etc/default/grub` |
| Registry holds boot parameters | Kernel cmdline in GRUB config |
| Event Viewer for boot events | `journalctl -b` |
| `bcdedit` to change behavior | Edit text file, then `sudo update-grub` |
| Safe Mode = minimal drivers + registry | Rescue = root shell + minimal services |
| Boot diagnostics = Win vivi RE | Boot diagnostics = `journalctl`, `dmesg`, single-user mode |

**Key takeaway:** Linux boot is fully transparent. Every parameter, message, and service start time is readable. Nothing hidden in a binary store.
