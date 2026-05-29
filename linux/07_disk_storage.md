# Module 7: Disk & Storage Management

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage disks and storage through:

```
Windows:
  - Disk Management (diskmgmt.msc) — visual partitioning/formats
  - diskpart — CLI partitioning tool
  - Get-Volume, Get-Disk — PowerShell storage cmdlets
  - Format-Volume — format drives
  - X:\ drive letters as mount points
  - \\server\share — SMB/CIFS network shares
  - Robocopy — file migration between volumes
```

Windows uses **drive letters** (C:, D:, E:) and **volume GUID paths** as mount points. Disks are partitioned in Disk Management or diskpart.

## The Shift

Linux uses a **unified mount tree** rooted at `/`. There are no drive letters — every mount point is a directory in the filesystem tree. The workflow is:

```
Discover → Partition → Format → Mount → Persist (fstab)
```

---

## Disks and Partitions

### Discovering Disks and Partitions

```bash
# List all block devices with filesystem info (Windows: Get-Disk + Get-Partition)
lsblk                           # Block device tree
lsblk -f                        # Include filesystem info
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT  # Custom columns

# Partition tables (Windows: diskpart → list partition)
fdisk -l                        # Partition table summary
fdisk -l /dev/sda               # Specific disk
parted -l                       # GNU parted (GPT-aware)

# Low-level info (Windows: Get-Disk | Format-List *)
blockdev --getsize64 /dev/sda   # Total size in bytes
blockdev --getss /dev/sda       # Sector size (bytes)
cat /proc/partitions             # Kernel's partition view
```

### Creating and Partitioning Disks

```bash
# Create GPT partition table (Windows: diskpart → convert gpt)
sudo parted /dev/sda mklabel gpt  # GPT = modern, >2TB, UEFI
sudo parted /dev/sda mklabel msdos  # MBR = legacy, ≤2TB limit

# Create partitions with parted (Windows: diskpart → create partition)
sudo parted /dev/sda mkpart primary ext4 1MiB 100%  # Single partition
sudo parted /dev/sda mkpart primary ext4 1MiB 50%   # 50% partition 1
sudo parted /dev/sda mkpart primary linux-swap 50% 100%  # 50% swap

# Or use fdisk (interactive, Windows: diskpart interactive)
sudo fdisk /dev/sda
# n → new partition → p → primary → enter (default first/last) → w → write
```

### Formatting Filesystems

```bash
# Format with filesystem (Windows: Format-Volume -FileSystem NTFS)
sudo mkfs.ext4 /dev/sda1         # ext4 — Linux default
sudo mkfs.xfs /dev/sda1          # XFS — RHEL/CentOS default
sudo mkfs.vfat -F 32 /dev/sda1   # FAT32 — USB cross-platform
sudo mkfs.ntfs /dev/sda1          # NTFS — Windows compatible

# With label (Windows: Format-Volume -FileSystemLabel "DATA")
sudo mkfs.ext4 -L "DATA" /dev/sda1
sudo e2label /dev/sda1 "BACKUP"   # Change label after format
sudo blkid /dev/sda1               # Verify label

# Create swap (Windows: New-Volume -FileSystem RAW + pagefile settings)
sudo mkswap /dev/sda2             # Create swap partition
sudo swapon /dev/sda2             # Enable swap
swapon --show                     # Check swap status
```

---

## Mounting and Unmounting

### Mounting Filesystems

```bash
# Mount a device (Windows: Mount-DiskImage / New-Volume)
sudo mount /dev/sdb1 /mnt/data    # Mount partition to directory
sudo umount /mnt/data             # Unmount (NOT unmount!)
sudo umount /dev/sdb1             # Unmount by device

# Mount with options (Windows: mountvol X: /parameters)
sudo mount -t ext4 /dev/sdb1 /mnt/data     # Force filesystem type
sudo mount -o ro /dev/sdb1 /mnt/data       # Mount read-only
sudo mount -o remount,rw /mnt/data         # Remount read-write
sudo mount -o bind /data /home/user/data   # Bind mount (mirror directory)

# Mount Windows share (Windows: New-SmbShare + net use)
sudo mount -t cifs //server/share /mnt/windows-share -o username=david,password=secret
sudo mount -t nfs server:/export /mnt/nfs-share   # NFS mount

# Loop mount (Windows: double-click .iso in Explorer)
sudo mount -o loop /tmp/ubuntu.iso /mnt/iso     # Mount ISO file
```

### View Mounts

```bash
# Show mounted filesystems (Windows: Get-Volume, Get-PSDrive)
df -h                               # Disk usage (human-readable)
df -i                               # Inode usage (critical!)
df -T                               # With filesystem type
mount                               # Mounted filesystems
findmnt                             # Hierarchical mount tree

# What's mounted where?
findmnt -T /mnt/data                # What's mounted at this path?
findmnt -S /dev/sdb1                # Where is /dev/sdb1 mounted?
lsblk -f                            # Block devices + mount points
```

### /etc/fstab — Permanent Mount Configuration

```bash
# fstab = Windows registry HKEY_LOCAL_MACHINE\SYSTEM\MountedDevices
# Where permanent mounts are stored
cat /etc/fstab
```

The **fstab** file defines persistent mounts. It's equivalent to Windows **diskpart persistent scripts** or the registry's mounted devices key.

```
# fstab format:
# <device>  <mount point>  <type>  <options>  <dump>  <pass>
UUID=xxxx-xxxx   /mnt/data   ext4   defaults     0       2
/dev/sdc1        /mnt/windows ntfs-3g defaults      0       0
//server/share   /mnt/backup  cifs   username=david,password=secret,nofail   0    0
none             /tmp         tmpfs  defaults     0       0
none             /dev/shm     tmpfs  defaults     0       0
```

| Field | Description | Windows Equivalent |
|-------|-------------|-------------------|
| `device` | `/dev/sda1` or `UUID=...` | Volume GUID path |
| `mount point` | Directory where mounted | Drive letter |
| `type` | ext4, xfs, vfat, cifs, tmpfs | NTFS, FAT32 |
| `options` | rw, ro, noauto, nofail, bind | mount parameters |
| `dump` | 0 = no backup, 1 = backup | — |
| `pass` | 0 = no fsck, 1 = root fsck, 2 = check | — |

```bash
# Common options (Windows: mount parameters)
#   rw        → Read-write
#   ro        → Read-only
#   noauto    → Don't auto-mount at boot
#   nofail    → Don't fail boot if device missing
#   defaults  → rw,suid,dev,exec,auto,nouser,async
#   bind      → Bind mount (mirror directory)
#   users     → Allow any user to mount/unmount

# Apply fstab changes (Windows: refresh mounted devices registry)
sudo mount -a                         # Mount ALL fstab entries
sudo findmnt --verify                 # Verify fstab syntax
```

---

## Disk Usage

### Checking Usage

```bash
# Disk space (Windows: Get-PSDrive -PSProvider FileSystem)
df -h                               # Filesystem disk space (human-readable)
df -i                               # Inode usage (check for exhaustion!)
df -T                               # With filesystem type column
df -h /                             # Root filesystem only

# Directory usage (Windows: Get-ChildItem C:\ -Recurse | Measure-Object Length)
du -sh /var/*                       # Per-directory usage
du -sh /home/*                      # Per-user usage
du --max-depth=1 /var/log           # Log directory breakdown

# Top offenders
du -sh /var/log/* | sort -rh | head -10  # 10 largest in /var/log
du -sh /home/* | sort -rh | head -10   # 10 largest users
```

### Finding Large Files

```bash
# Large files (Windows: Get-ChildItem -Recurse | Sort-Object Length)
find / -type f -size +100M 2>/dev/null          # Files >100MB
find /var -type f -name "*.log" -size +50M      # Large log files
find /tmp -type f -atime +7 -delete             # Delete >7 day old temp files
find /var/cache -type f -delete                 # Clean cache
find /home -type f -name "*.core"               # Core dumps
```

### Critical Inode Check

```bash
# Inode exhaustion (Windows doesn't have this problem)
df -i                               # Shows inode usage
# If inode usage is 100%: files exist but you can't create new ones
# Fix: find and delete many small files
find /var/spool -type f -delete     # Or similar
```

---

## LVM — Logical Volume Management

```bash
# LVM (Windows: Storage Spaces / Dynamic Disks)
# Layering: Physical Volume → Volume Group → Logical Volume
# Like Storage Spaces but with snapshots and live resize
```

### LVM Commands

```bash
# View LVM (Windows: Get-Volume)
pvs                                 # Physical Volumes
vgs                                 # Volume Groups
lvs                                 # Logical Volumes
vgdisplay                           # Detailed VG info
lvdisplay                           # Detailed LV info

# Create LVM (Windows: New-StoragePool + New-Volume)
sudo pvcreate /dev/sdb              # Create physical volume
sudo vgcreate vgdata /dev/sdb       # Create volume group
sudo lvcreate -L 50G -n lvdata vgdata  # Create 50GB logical volume
sudo mkfs.ext4 /dev/vgdata/lvdata   # Format it
sudo mount /dev/vgdata/lvdata /mnt/data  # Mount it

# Extend a logical volume (Windows: Resize-Volume)
sudo lvextend -L +20G /dev/vgdata/lvdata   # Add 20GB
sudo resize2fs /dev/vgdata/lvdata       # Resize filesystem (ext4)
sudo xfs_growfs /mnt/data             # Resize filesystem (XFS)

# Shrink (ext4 only, must unmount first — XFS can't shrink!)
sudo umount /mnt/data
sudo resize2fs /dev/vgdata/lvdata 40G
sudo lvreduce -L 40G /dev/vgdata/lvdata
sudo mount /dev/vgdata/lvdata /mnt/data

# Remove LVM (Windows: Remove-Volume)
sudo umount /mnt/data
sudo lvremove /dev/vgdata/lvdata
sudo vgremove vgdata
sudo pvremove /dev/sdb
```

---

## tmpfs — Memory Filesystems

```bash
# tmpfs = RAM-backed filesystem (Windows: RAM disk, C:\Windows\Temp)
# Fastest storage — lost on reboot
```

```bash
# tmpfs mounts
df -h | grep tmpfs                # Show tmpfs mounts
ls -lh /tmp                       # /tmp is often tmpfs
ls -lh /dev/shm                   # Shared memory filesystem

# Create tmpfs (Windows: New-PSDrive -Root RAM: -PSProvider FileSystem)
sudo mount -t tmpfs -o size=2G tmpfs /mnt/ramdisk
echo "hello" > /mnt/ramdisk/test.txt
dd if=/dev/zero of=/mnt/ramdisk/bigfile bs=1M count=500  # Extremely fast!
```

---

## Hands-On Exercise

```bash
# 1. View disks and filesystems
lsblk -f
df -h
df -i                               # Critical — check for inode exhaustion

# 2. Find large files and directories
find /var -type f -size +10M 2>/dev/null | head -10
du -sh /var/* | sort -rh | head -5

# 3. Create a test partition (on a test disk!):
sudo fdisk /dev/sdb                 # Interactive: n → p → 1 → enter → enter → w
sudo mkfs.ext4 /dev/sdb1            # Format it
sudo mkdir -p /mnt/testdisk          # Create mount point
sudo mount /dev/sdb1 /mnt/testdisk   # Mount it
df -h | grep testdisk             # Verify mount

# 4. Make it persistent (fstab):
sudo blkid /dev/sdb1               # Get UUID
echo 'UUID=<uuid> /mnt/testdisk ext4 defaults 0 2' | sudo tee -a /etc/fstab

# 5. Test fstab (without rebooting):
sudo mount -a                       # Should mount without errors
findmnt -S /dev/sdb1              # Verify mount

# 6. LVM if available:
sudo pvs
sudo vgs
sudo lvs
sudo lvextend -L +1G /dev/ubuntu-vg/ubuntu-lv   # Extend if LVM exists
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv         # Resize filesystem

# 7. Clean up (if you created test mount):
sudo umount /mnt/testdisk
# Remove the fstab entry you added

# 8. Check disk health (SMART if available):
sudo smartctl -a /dev/sda           # Requires smartmontools package
```

---

## Mental Model Shift

| Windows Storage Mindset | Linux Storage Mindset |
|--|--|
| Drive letters (C:, D:, E:) | Mount points are directories (`/mnt/data`) |
| Disk Management GUI (diskmgmt.msc) | `lsblk` + `fdisk` + `parted` (CLI only) |
| Format-Volume → auto | `mkfs.ext4` / `mkfs.xfs` (manual format) |
| New-Volume → auto mount point | `mkdir` + `mount` (you create the mount point) |
| Mount-SmbShare → UNC path | `mount -t cifs` → directory mount |
| Get-Volume | `df -h` + `mount` + `findmnt` |
| Storage Spaces (RAID) | LVM (PV → VG → LV) |
| DiskPart CLI | `fdisk` / `parted` (CLI only) |
| Persistent mount = drive letter | `/etc/fstab` (text file, like `/etc/resolv.conf`) |
| NTFS labels in Explorer | `e2label` + `blkid` |
| Disk Cleanup → Recycle Bin | `du` + `find` + `delete` + `apt clean` |
| VSS (Volume Shadow Copy) | LVM snapshots (`lvcreate -s`) |
| Disk quotas via GPO | `quotacheck` + `setquota` |
| One mounted ISO image | `mount -o loop` (any file as device) |
| One manager (Disk Management) | Many tools: `lsblk`, `fdisk`, `parted`, `mkfs`, `mount`, `blkid` |

**Key takeaway:** Linux storage is **directory-based** — mount a device to a directory, not a drive letter. The workflow is always: **partition (`fdisk`/`parted`) → format (`mkfs`) → mount (`mount`) → persist (`/etc/fstab`)**. Unlike Windows where drive letters auto-mount, Linux requires explicit mount points. `lsblk` shows devices, `df -h` shows usage, `mount`/`findmnt` shows what's mounted, and `/etc/fstab` persists mounts. LVM adds abstraction (PV → VG → LV) but the core concepts match Windows Storage Spaces. **Always check `df -i` for inode exhaustion** (a classic Linux gotcha) and remember: **LVM resize needs two steps** — extend the volume **then** resize the filesystem (`resize2fs` for ext4, `xfs_growfs` for XFS).
