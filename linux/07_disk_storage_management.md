# Module 7: Disk & Storage Management

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage storage through:

```
Windows Storage:
  diskmgmt.msc                    # Disk Management GUI
  diskpart                        # CLI partitioning tool
  Get-Disk, Get-Partition, Get-Volume  # PowerShell cmdlets
  Format-Volume, New-Volume       # Create/manage volumes
  Mount-SmbShare, net share       # Network shares
  X:\Volume GUID path              # Volume mount to drive letter
  \\server\share                   # UNC network path
  Robocopy                        # Migrate files between volumes
```

Windows uses **drive letters** (C:, D:, E:) for volume mounts and **Disk Management** for partitioning. Volumes are auto-formatted to NTFS/exFAT.

## The Shift

Linux mounts storage to **directories** instead of drive letters. The entire filesystem is one **tree** rooted at `/`. Storage is **layered** — you must partition → format → mount in sequence. There's no automatic drive letter assignment.

```bash
# Windows: X:\ → drive letter mount
# Linux: /mnt/data → directory mount

# The mount tree:
/
├── bin, sbin   # Core system binaries
├── etc         # Configuration files
├── var         # Variable data (logs, caches)
├── home          # User home directories
├── tmp          # Temporary files
├── mnt          # Manual mount point (your external drives)
├── opt          # Optional software (Windows: C:\Program Files)
└── dev          # Device files (not real files!)
```

### Viewing Disks & Partitions

```bash
# View disk layout (Windows: Get-Disk, Get-Partition)
lsblk -f                          # List block devices with filesystem info
fdisk -l                          # List partition tables (like diskpart)
lsblk -a                          # List ALL devices (including empty)
fdisk -l /dev/sda                 # Specific disk

# View mounted filesystems (Windows: Get-Volume, Get-PSDrive)
df -h                           # Disk usage (human-readable)
df -i                           # Inode usage (inode exhaustion!)
mount                         # Mounted filesystems (same as cat /etc/mtab)
findmnt                        # Hierarchical mount view
lsblk -f | column -t           # Neat column output

# Detailed info (Windows: Get-Disk | Format-List *)
blockdev --getsize64 /dev/sda   # Disk size in bytes
blockdev --getss /dev/sda       # Sector size
cat /proc/partitions             # Kernel's partition table
```

### Creating & Formatting Partitions

```bash
# Create a partition (Windows: diskpart → create partition)
sudo parted /dev/sda mklabel gpt  # Create GPT partition table
sudo parted /dev/sda mkpart primary ext4 1MiB 100%  # Create partition

# Or use fdisk (interactive, Windows: diskpart)
sudo fdisk /dev/sda               # Interactive partitioning
# Commands: n=new, p=primary, w=write, t=change type, d=delete

# Create filesystem (Windows: Format-Volume -FileSystem NTFS)
sudo mkfs.ext4 /dev/sda1          # Create ext4 filesystem
sudo mkfs.xfs /dev/sda1           # Create XFS filesystem
sudo mkfs.vfat /dev/sda1          # Create FAT32 (USB, cross-platform)
sudo mkfs.ntfs /dev/sda1          # Create NTFS (Windows compatible)

# Format options explained:
# -t ext4 → ext4 filesystem (default on Ubuntu)
# -t xfs → XFS filesystem (default on RHEL)
# -t vfat → FAT32 (USB sticks, cross-platform)
# -L "label" → Volume label (like drive label in Windows)
sudo mkfs.ext4 -L "DATA" /dev/sda1

# Create swap space (Windows: Pagefile)
sudo mkswap /dev/sda2             # Create swap partition
sudo swapon /dev/sda2             # Enable swap
swapon --show                     # Check swap status
```

### Mounting & Unmounting

```bash
# Mount a device (Windows: New-Volume / diskpart assign)
sudo mount /dev/sdb1 /mnt/data    # Mount partition to directory
sudo umount /mnt/data             # Unmount (NOT unmount!)

# See what's mounted (Windows: Get-Volume)
findmnt                           # Tree view of mounted filesystems
findmnt -T /mnt/data              # What's mounted at this path?
findmnt -S /dev/sdb1              # Where is this device mounted?

# Mount options (Windows: mountvol X: /new)
sudo mount -t ext4 /dev/sdb1 /mnt/data  # Force filesystem type
sudo mount -o ro /dev/sdb1 /mnt/data  # Mount read-only
sudo mount -o remount,rw /mnt/data   # Remount read-write
sudo mount -o bind /data /home/user/data  # Bind mount (mirror directory)

# Mount Windows shares (Windows: net use Z: \\server\share)
sudo mount -t cifs //server/share /mnt/windows-share -o username=david,password=secret
sudo mount -t nfs server:/export /mnt/nfs-share   # NFS mount

# List all mountable filesystems
blkid                             # Block device IDs and filesystem types
```

### /etc/fstab — Permanent Mount Configuration

```bash
# fstab (Windows: registry key HKEY_LOCAL_MACHINE\SYSTEM\MountedDevices)
# Where permanent mounts are stored (Windows: registry + Disk Management)
cat /etc/fstab                    # View current fstab
sudo blkid                        # Get UUID for fstab entries
sudo nano /etc/fstab              # Edit fstab (or use visudo-style: mountctl)

# fstab format (Windows: registry key-value pairs)
# UUID=xxxx-xxxx  /mnt/data  ext4  defaults  0  2
# ^^^^         ^^^^   ^^^^    ^^^^^  ^^^^^^   ^  ^
# UUID         mount  filesystem  options   dump  fsck
# (device)     point  type       (rw,ro,noauto)  (0=off)  (0=off, 1=root, 2=others)

# Example fstab entries (Windows: Disk Management persistent mount)
UUID=1234-5678    /mnt/data     ext4    defaults,noauto    0  2
UUID=abcde-fghi    /boot        ext4    defaults            0  1
/dev/sdc1          /mnt/windows  ntfs-3g  defaults          0  0
//server/share     /mnt/backup   cifs   username=david,password=secret,nofail  0  0
none            /proc        proc   defaults          0  0
none            /sys          sysfs   defaults          0  0
none            /dev           devtmpfs  defaults          0  0
none            /tmp           tmpfs   defaults        0  0

# Options (Windows: Disk Management mount options)
#   rw         → Read-write
#   ro         → Read-only
#   noauto     → Don't auto-mount at boot
#   nofail     → Don't fail boot if device missing
#   defaults   → rw,suid,dev,exec,auto,nouser,async
#   bind       → Bind mount (mirror)
#   loop       → Mount as loop device (ISO, image)
#   users      → Allow any user to mount/unmount

# Apply fstab changes (Windows: refresh disk management)
sudo mount -a                         # Mount ALL fstab entries
sudo findmnt --verify                 # Verify fstab is valid
sudo mount /dev/sdb1                  # Mount specific entry (uses fstab)
```

### Disk Usage & Space Management

```bash
# Disk usage (Windows: Get-PSDrive -PSProvider FileSystem)
df -h                               # Filesystem disk space usage
df -i                               # Inode usage (important!)
du -sh /var/*                       # Disk usage per directory
du -sh /home/*                      # Disk usage per user
du --max-depth=1 /var/log           # Log directory analysis
du -sh /var/log/* | sort -rh | head -10  # Top 10 largest log files

# Find large files (Windows: Get-ChildItem -Recurse | Sort-Object Length | Select -Last 10)
find / -type f -size +100M 2>/dev/null          # Files larger than 100MB
find /var -type f -name "*.log" -size +50M      # Large log files
find /home -type f -name "*.core" -o -name "*.tmp"   # Core dumps, temp files

# Find old files (Windows: Get-ChildItem | Where-Object {$_.LastWriteTime -lt ...})
find /var/log -type f -mtime +30               # Files modified more than 30 days ago
find /tmp -type f -atime +7 -delete            # Delete files not accessed in 7 days
find /var/cache -type f -delete                # Clean cache
```

### LVM — Logical Volume Management

```bash
# LVM (Windows: Storage Spaces / Dynamic Disks)
# Layering: Physical Volume → Volume Group → Logical Volume
# Like Storage Spaces but more granular

# List LVM volumes (Windows: Get-Volume)
pvs                               # Physical Volumes
vgs                               # Volume Groups
lvs                               # Logical Volumes

# Create an LVM setup (Windows: New-Volume -StoragePool)
sudo pvcreate /dev/sdb            # Create physical volume
sudo vgcreate vgdata /dev/sdb     # Create volume group named vgdata
sudo lvcreate -L 50G -n lvdata vgdata  # Create 50GB logical volume
sudo mkfs.ext4 /dev/vgdata/lvdata # Format it
sudo mount /dev/vgdata/lvdata /mnt/data  # Mount it

# Extend a volume (Windows: Resize-Volume)
sudo lvextend -L +20G /dev/vgdata/lvdata  # Add 20GB
sudo resize2fs /dev/vgdata/lvdata    # Resize filesystem to fill volume
sudo xfs_growfs /mnt/data         # For XFS volumes

# Shrink an XFS volume (Windows: Resize-Volume)
sudo xfs_growfs /mnt/data         # XFS can only grow! (need to format to shrink)

# Remove LVM (Windows: Remove-Volume)
sudo umount /mnt/data
sudo lvremove /dev/vgdata/lvdata
sudo vgremove vgdata
sudo pvremove /dev/sdb
```

### Disk Partitions & Labels

```bash
# Partition table types (Windows: diskpart → convert mbr → convert gpt)
# MBR (DOS) → Old, max 2TB, max 4 primary partitions
# GPT → New, max 18EB, 128 partitions, UEFI required

# View partition info (Windows: diskpart → list volume)
lsblk -f                          # Block devices with filesystems
fdisk -l                          # Partition tables
blkid                             # UUIDs and filesystem types
gdisk -l /dev/sda                 # GPT partition table (gdisk)

# Partition labels (Windows: Set-Volume -NewFileSystemLabel)
sudo e2label /dev/sda1 "DATA"     # Set ext4 label
sudo blkid                        # Verify label
sudo tune2fs -L "DATA" /dev/sda1  # Alternative label setter

# Partition types (Windows: diskpart → type codes)
# 83 = Linux filesystem
# 82 = Linux swap
# 8e = Linux LVM
# ef = EFI System Partition
# 07 = NTFS/HPFS
# de = Dell Utility
```

### tmpfs — Memory-Based Filesystems

```bash
# tmpfs (Windows: C:\Windows\Temp, ramdisk tools)
# Stores data in RAM (faster than disk, but lost on reboot)

df -h | grep tmpfs                # Show tmpfs mounts
ls -lh /tmp                       # /tmp is often tmpfs
ls -lh /dev/shm                   # Shared memory filesystem

# Create a tmpfs mount (Windows: New-PSDrive -PSProvider FileSystem -Root RAM:)
sudo mount -t tmpfs -o size=2G tmpfs /mnt/ramdisk
echo "hello" > /mnt/ramdisk/test.txt
dd if=/dev/zero of=/mnt/ramdisk/bigfile bs=1M count=500  # Fast!

# /dev/shm — shared memory (like tmpfs but for IPC)
ls -lh /dev/shm                   # Shared memory files
```

## Hands-On Exercise

```bash
# 1. View your disks and filesystems
lsblk -f
df -h
df -i                              # Check for inode exhaustion

# 2. Find large files
find /var -type f -size +10M 2>/dev/null | head -10
du -sh /var/* | sort -rh | head -5

# 3. Create a partition (on test disk!):
sudo fdisk /dev/sdb                # Interactive: n, p, 1, enter, enter, w
sudo mkfs.ext4 /dev/sdb1           # Format it
sudo mkdir -p /mnt/testdisk          # Create mount point
sudo mount /dev/sdb1 /mnt/testdisk   # Mount it
df -h | grep testdisk             # Verify mount

# 4. Add to fstab (make it persistent):
sudo blkid /dev/sdb1               # Get UUID
echo 'UUID=<your-uuid> /mnt/testdisk ext4 defaults 0 2' | sudo tee -a /etc/fstab

# 5. Test fstab (without rebooting):
sudo mount -a                      # Should mount without errors
findmnt -S /dev/sdb1              # Verify mount

# 6. LVM if available:
sudo pvs
sudo vgs
sudo lvs
sudo lvextend -L +1G /dev/ubuntu-vg/ubuntu-lv   # Extend if LVM exists
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv      # Resize filesystem

# 7. Clean up (if you created test mount):
sudo umount /mnt/testdisk
# Remove the fstab entry you added

# 8. Check disk health (SMART info if available):
sudo smartctl -a /dev/sda          # Requires smartmontools
```

## Mental Model Shift

| Windows Storage Mindset | Linux Storage Mindset |
|------|------|--|
| Drive letters (C:, D:, E:) | Mount to directories (/mnt/data) |
| Disk Management GUI (diskmgmt.msc) | lsblk, fdisk, parted (CLI only) |
| Format-Volume -FileSystem NTFS | mkfs.ext4, mkfs.xfs, mkfs.vfat |
| New-Volume → auto-creates mount point | mkdir + mount (manual mount point) |
| Mount-SmbShare → UNC path | mount -t cifs → directory mount |
| Get-Volume | df -h + mount + findmnt |
| Storage Spaces (RAID) | LVM (more powerful, different layering) |
| DiskPart CLI | fdisk/parted (CLI only) |
| Persistent mounts = drive letters | /etc/fstab (text file, like /etc/resolv.conf) |
| NTFS labels in Explorer | e2label, blkid |
| Disk Cleanup → Recycle Bin | du, find + delete, apt clean |
| VSS (Volume Shadow Copy) | LVM snapshots (lvcreate -s) |
| Disk quotas via GPO | quota tools (quotacheck, setquota) |
| Mounted ISO images (right-click → Mount) | mount -o loop |
| One manager (Disk Management) | Multiple tools (lsblk, fdisk, parted, mkfs, mount, blkid) |

**Key takeaway:** Linux storage is **directory-based** — you mount a device to a directory, not a drive letter. The workflow is always: **partition (fdisk/parted) → format (mkfs) → mount (mount) → persist (/etc/fstab)**. Unlike Windows where drive letters auto-mount, Linux requires explicit mount points. `lsblk` shows devices, `df -h` shows usage, `mount`/`findmnt` shows what's mounted, and `/etc/fstab` persists mounts. LVM adds abstraction (PV → VG → LV) but the core concepts are the same as Windows Storage Spaces: partitions, volumes, filesystems. Always check `df -i` for inode exhaustion (a common Linux pitfall) and never forget to run `resize2fs`/`xfs_growfs` after extending an LVM volume.
