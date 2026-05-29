# Module 12: Disk & Storage

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage storage through:

```
Windows:
  Disk Management (diskmgmt.msc) → GUI for disks/partitions
  Diskpart → CLI disk management
  Get-Disk → List disks
  Get-Partition → List partitions
  Get-Volume → List volumes
  Get-PhysicalDisk → Physical disk info
  Get-DiskPartLog → Diskpart log
  Format-Volume → Format volumes
  New-Volume → Create volumes
  Expand-Volume → Extend volumes
  Get-StoragePool → Storage pools
  Get-ResilienceGroup → Storage spaces
  storport, diskraid → Storage drivers
  wmic diskdrive list → WMI disk info
  wmic volume list → WMI volume info
```

Windows manages storage via **disk objects → partitions → volumes (drive letters) → filesystems**, with storage spaces (RAID/LVM equivalent) for advanced pooling. Drive letters (C:, D:, E:) provide simple mount points.

## The Shift

Linux uses a **unified device naming scheme** (`/dev/sda`, `/dev/nvme0n1`) and **mount points** (directories) instead of drive letters. Linux storage is organized as **devices → partitions → LVs (LVM) → filesystems → mount points**. Unlike Windows which uses drive letters (C:, D:), Linux mounts every filesystem **under a directory** — even the root filesystem `/`. Linux LVM (Logical Volume Manager) provides **dynamic resizing** without rebooting, whereas Windows requires disk management or diskpart. The key insight: **everything is mounted** — USB drives, network shares, CD-ROMs all appear as directories under `/`.

---

## Disk Detection & Identification

### Physical Disks

```bash
# Physical disk info (Windows: Get-PhysicalDisk, Get-Disk)
lsblk                              # List block devices (Windows: Get-Disk | Format-List)
lsblk -f                           # With filesystem info (Windows: Get-Volume | Format-List)
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,MODEL  # Custom columns
fdisk -l                           # Partition tables (Windows: diskpart → list disk)
parted -l                          # Partition info (Windows: diskpart → list disk)
cat /proc/partitions               # Kernel partition table
smartctl -a /dev/sda               # SMART disk health (Windows: Get-PhysicalDisk | Select-Object HealthStatus)
sudo apt install smartmontools     # Install smartctl
lshw -class disk                   # Detailed disk hardware info
lspci | grep -i -A4 -B4 -C1 storage  # PCI storage controller

# Disk details (Windows: Get-PhysicalDisk | Format-List)
lsblk -d                           # Disks only (no partitions)
lsblk -r                           # Raw output (for scripting)
sg_inq /dev/sda                    # SCSI inquiry (device info)
hdparm -I /dev/sda                 # ATA device info
```

### Disk Partitions

```bash
# Partition tables (Windows: diskpart → list disk → detail disk)
fdisk -l                           # List partitions
fdisk /dev/sda                     # Interactive (Windows: diskpart)
fdisk -l /dev/sda                  # Summary
fdisk -l /dev/sdb                  # Another disk
parted /dev/sda print              # Print partition table (Windows: diskpart → detail disk)
sfdisk -l                          # Quick summary of all partitions
sfdisk -d /dev/sda                 # Partition dump (for backup/restore)
gdisk -l /dev/sda                  # GPT partition table

# Partition types (Windows: diskpart → detail disk → partition type)
file -sL /dev/sda1                 # Filesystem type of a partition
blkid                              # All partitions with UUIDs (Windows: Get-Volume | Format-List)
tune2fs -l /dev/sda1               # Ext filesystem info (Windows: Get-Partition | Format-List)
```

---

## Volume Management

### LVM (Logical Volume Manager)

```bash
# LVM concepts (Windows: Storage Spaces — disk pools, mirror, parity)
# LVM layers:
#   PV (Physical Volume) = physical disk/partition (= physical disk in Storage Spaces)
#   VG (Volume Group) = pool of PVs (= storage pool)
#   LV (Logical Volume) = formatted volume (= virtual disk)

# LVM overview (Windows: Get-StoragePool, Get-ResilienceGroup, Get-VirtualDisk)
pvs                                # Physical volumes
vgs                                # Volume groups
lvs                                # Logical volumes
vgdisplay                          # VG details (Windows: Get-StoragePool | Format-List)
lvdisplay                          # LV details (Windows: Get-VirtualDisk | Format-List)
pvdisplay                          # PV details (Windows: Get-PhysicalDisk | Format-List)
lvs -a                             # All LVs including snapshots
vgs -o +lv_count,pv_count          # VGs with counts
```

### LVM Operations

```bash
# Create LVM (Windows: New-StoragePool, New-VirtualDisk)
# 1. Create PV
pvcreate /dev/sdb1                 # Create physical volume
# 2. Create VG
vgcreate vg_data /dev/sdb1         # Create volume group
# 3. Create LV
lvcreate -L 10G -n lv_data vg_data  # 10GB LV named "lv_data"
# 4. Format and mount
mkfs.ext4 /dev/vg_data/lv_data
mount /dev/vg_data/lv_data /mnt/data

# Resize (Windows: Expand-Volume — requires diskmgmt.msc)
lvextend -L +5G /dev/vg_data/lv_data  # Extend LV by 5GB
resize2fs /dev/vg_data/lv_data    # Resize ext filesystem
lvreduce -L -2G /dev/vg_data/lv_data  # Shrink LV
resize2fs /dev/vg_data/lv_data    # Resize ext filesystem (must shrink filesystem first!)

# Remove LVM (Windows: Remove-StoragePoolMember, Remove-VirtualDisk)
umount /dev/vg_data/lv_data
lvremove /dev/vg_data/lv_data
vgremove vg_data
pvremove /dev/sdb1

# Snapshot (Windows: VssAdmin create shadows or Get-Volume | Select-Object isReadOnly)
lvcreate -s -L 1G -n snap_lv_data vg_data/lv_data
```

---

## Filesystem Management

### Create & Format

```bash
# Filesystem creation (Windows: Format-Volume -FileSystem NTFS)
mkfs.ext4 /dev/sdb1                # Create ext4 filesystem
mkfs.xfs /dev/sdb1                 # Create XFS filesystem
mkfs.vfat /dev/sdb1                # Create FAT32 filesystem (USB)
mkfs.ntfs /dev/sdb1                # Create NTFS filesystem (install ntfs-3g)
mkfs.btrfs /dev/sdb1               # Create Btrfs filesystem

# Filesystem info (Windows: Get-Volume | Format-List)
blkid /dev/sdb1                    # UUID and type
tune2fs -l /dev/sdb1               # Ext filesystem details
xfs_info /dev/sdb1                 # XFS filesystem details
df -T                              # Show filesystem type
```

### Mount & Unmount

```bash
# Mounting (Windows: New-PSDrive, mountvol)
mount /dev/sdb1 /mnt/data          # Mount a partition
mount -t ext4 /dev/sdb1 /mnt/data  # Specify filesystem type
mount -o ro /dev/sdb1 /mnt/data    # Mount read-only
mount -o remount,rw /mnt/data      # Remount read-write
umount /mnt/data                   # Unmount
umount /dev/sdb1                   # Unmount by device
umount -l /dev/sdb1                # Lazy unmount (when busy)
df -h                              # Show all mounted filesystems (Windows: Get-Volume | Format-List)
findmnt                            # Find mount points (Windows: Get-Volume | Where-Object MountPoint)

# /etc/fstab — automatic mounting (Windows: Registry HKLM\SYSTEM\CurrentControlSet\Services)
cat /etc/fstab                     # Persistent mount config
echo "/dev/sdb1 /mnt/data ext4 defaults 0 2" >> /etc/fstab  # Add mount entry
mount -a                           # Mount all fstab entries (Windows: mountvol /s)

# fstab fields (Windows: diskpart → assign mount=C:\)
# /dev/sdb1  /mnt/data  ext4  defaults  0  2
# device    mountpoint  fs    options   dump  fsck

# Mount options (Windows: Format-Volume -FileSystemOptions)
defaults                             # rw,suid,dev,exec,auto,nouser,async
noexec                               # Don't execute binaries
nosuid                               # Ignore setuid/setgid
nodev                              # Don't interpret device files
ro                                   # Read-only
rw                                   # Read-write (default)
auto                                 # Mount at boot (default)
noauto                               # Don't mount at boot
user                                 # Allow any user to mount
nouser                               # Only root can mount
nofail                               # Don't fail boot if device missing
```

### USB Drives

```bash
# USB drives (Windows: Plug-and-play with drive letter assignment)
# USB drives auto-mount in GUI (GNOME/KDE), or use:
lsusb                              # List USB devices
udisksctl mount --block /dev/sdc1  # Mount USB drive (CLI)
udisksctl unmount --block /dev/sdc1 # Unmount USB drive (CLI)
udisksctl status                   # All removable devices
```

---

## Disk Usage & Monitoring

### Usage Analysis

```bash
# Disk usage (Windows: Get-Volume, Get-ChildItem -Recurse)
df -h                              # All volumes, human-readable (Windows: Get-Volume | Format-Table)
df -i                              # Inode usage (Windows: wmic filesystem get Name,BlockSize,FreeSpace)
du -sh /var/log/*                  # Directory sizes (Windows: Get-ChildItem -Recurse | Sort-Object Length -Descending)
du -sh /home/*                     # User directory sizes
du -sh /*                          # Root directory sizes
du --max-depth=1 /var              # One level deep
ncdu /var                          # Interactive disk usage (install: sudo apt install ncdu)
du -sh --exclude=/proc --exclude=/sys /*  # Exclude virtual filesystems
```

### Inode Management

```bash
# Inodes (Windows: no direct equivalent — NTFS uses MFT entries)
df -i                              # Inode usage (Windows: wmic filesystem get Name,BlockSize,FreeSpace)
find / -xdev -type f -empty        # Empty files
find / -xdev -name ".*"            # Hidden files
```

### I/O Performance

```bash
# Disk I/O performance (Windows: Get-Counter "\PhysicalDisk(*)\*", Get-PhysicalDisk | Select-Object ReadLatency,WriteLatency)
iostat -x 1 10                     # Detailed I/O stats (install: sudo apt install sysstat)
iostat -d 1 10                     # Disk-only stats
iostat -h                          # Human-readable
iotop                              # Real-time I/O (install: sudo apt install iotop)
hdparm -tT /dev/sda                # Disk read performance test
```

---

## Storage Pools & Advanced

### ZFS (Advanced Pooling)

```bash
# ZFS (Windows: Storage Spaces with mirror/raidz)
apt install zfsutils-linux         # Install ZFS
zpool create mypool /dev/sdb /dev/sdc  # Create pool (Windows: New-StoragePool -StoragePoolFriendlyName "pool" -FriendlyName "data")
zpool list                         # List pools (Windows: Get-StoragePool)
zpool status                       # Pool health (Windows: Get-PhysicalDisk | Select-Object HealthStatus)
zfs create mypool/data             # Create dataset (Windows: New-VirtualDisk -StoragePoolFriendlyName "pool")
zfs list                           # List datasets (Windows: Get-VirtualDisk)
zfs destroy mypool/data            # Remove dataset
zpool destroy mypool               # Destroy pool
zpool import                         # Import pools (USB/external)
zpool export mypool                # Export pool safely
zfs send mypool/data | zfs recv otherpool/data  # ZFS replication
```

### RAID (Hardware/Software)

```bash
# RAID management (Windows: Storage Spaces — simple, mirror, parity, raid5, raid6)
mdadm --detail /dev/md0            # Check software RAID (Windows: Get-PhysicalDisk -PhysicalMedia RAID)
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc  # Create RAID1 mirror
mdadm --detail --scan >> /etc/mdadm/mdadm.conf  # Save config
mdadm --stop /dev/md0              # Stop RAID array
mdadm --assemble /dev/md0 /dev/sdb /dev/sdc  # Assemble array
cat /proc/mdstat                   # RAID status (Windows: Get-PhysicalDisk | Where-Object HealthStatus -eq 'healthy')
```

### Network Shares

```bash
# Network shares (Windows: New-SmbShare, New-PSDrive, mount-smb)
# Mounting NFS
mount -t nfs server:/share /mnt/nfs   # Mount NFS share
showmount -e server                   # List NFS exports

# Mounting CIFS/SMB
sudo apt install cifs-utils           # Install CIFS utilities
mount -t cifs //server/share /mnt/smb -o username=user,password=pass  # Mount SMB share
echo "//server/share /mnt/smb cifs credentials=/etc/samba/credentials,uid=1000,gid=1000 0 0" >> /etc/fstab  # Persistent

# CIFS credentials file (Windows: net use /savecred)
sudo nano /etc/samba/credentials
# username=admin
# password=secret
chmod 600 /etc/samba/credentials      # Secure credentials
```

---

## Hands-On Exercise

```bash
# 1. Disk overview
lsblk                              # All block devices
lsblk -f                           # With filesystems
lsblk -d                           # Disks only
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT

# 2. Partition table
fdisk -l                           # All partitions
parted -l                          # Partition details
blkid                              # UUIDs

# 3. Disk usage
df -h                              # Volumes overview
du -sh /*                          # Root directory sizes
du -sh /var/*                      # Var directory sizes
ncdu /var                          # Interactive (install ncdu)
iostat -x 1 5                      # I/O stats (install sysstat)

# 4. Filesystem management
cat /etc/fstab                     # Persistent mounts
mount -a                           # Mount all fstab entries
mount | grep /mnt                  # Check /mnt mounts

# 5. LVM (if available)
pvs                                # Physical volumes
vgs                                # Volume groups
lvs                                # Logical volumes
vgdisplay                          # VG details
lvdisplay                          # LV details

# 6. SMART disk health
sudo smartctl -a /dev/sda          # Disk health
```

---

## Mental Model Shift

| Windows Storage Mindset | Linux Storage Mindset |
|--|--|
| Disk Management GUI (diskmgmt.msc) | `lsblk` + `fdisk -l` + `df -h` (CLI) |
| Get-PhysicalDisk | `lsblk -d` or `smartctl -a /dev/sda` |
| Get-Disk + Get-Partition + Get-Volume | `lsblk` (all-in-one command) |
| diskpart → create partition → format | `fdisk` → `mkfs.ext4` → `mount` |
| Get-Volume → drive letters (C:, D:) | `df -h` → mount points (/home, /data) |
| New-Volume → assigns drive letter | `mkfs.ext4` + `mount` + `/etc/fstab` |
| Expand-Volume → extends partition | `lvextend` + `resize2fs` (LVM) |
| Storage Spaces pools | `vgcreate` (LVM) or `zpool create` (ZFS) |
| Storage Spaces mirrors/RAID | `mdadm` or ZFS raidz/mirror |
| Format-Volume -FileSystem NTFS | `mkfs.ext4` or `mkfs.xfs` or `mkfs.vfat` |
| Get-Volume | Format-List | `lsblk -f` or `df -h` |
| Disk space via Properties GUI | `df -h` and `du -sh` (CLI) |
| Disk cleanup tool | `ncdu` or `du -sh` (CLI) |
| USB auto-mount with drive letter | USB auto-mount in GUI or `udisksctl mount` |
| Mount-SmbShare | `mount -t cifs //server/share /mnt/smb` |
| New-SmbShare (SMB server) | `exportfs /etc/exports` (NFS) or `smbd` (Samba) |
| wmic volume list | `blkid` |
| Get-Volume | Where-Object SizeRemaining | `df -h \| grep /data` |
| Diskpart log (C:\Windows\diskpart_log.txt) | `dmesg \| grep -i "sda\|sd\|nvme"` |
| Format-Volume -AllocationUnitSize 64KB | `mkfs.ext4 -F -F -b 4096 -E stride=16 /dev/sdb1` |
| Get-PhysicalDisk | Select-Object HealthStatus | `smartctl -a /dev/sda \| grep -i "health\|temperature"` |
| Get-PhysicalDisk | Where-Object MediaType -eq "SSD" | `lsblk -d -o NAME,ROTA \| grep "0"` (0=SSD, 1=HDD) |
| Diskpart → assign mount=C:\ | `echo "/dev/sdb1 /mnt/data ext4 defaults 0 2" >> /etc/fstab` |
| Diskpart → assign mount=none (no drive letter) | No equivalent — Linux requires mount point |
| Diskpart → remove mount=C: | `umount` + remove from `/etc/fstab` |
| Get-Volume | Format-List | `df -Th` (size + type) |
| Format-Volume → NTFS → Windows only | `mkfs.ext4` → Linux only, `mkfs.vfat` → all platforms |
| Format-Volume → exFAT → cross-platform | `mkfs.vfat -F 4` → exFAT |
| Disk management → "Refresh" | `lsblk -f` or `partprobe` |
| DiskPart log for troubleshooting | `dmesg \| grep sd` or `journalctl -k \| grep sd` |

**Key takeaway:** Linux storage management is **CLI-driven** — use `lsblk` as your primary disk overview tool (replaces `Get-PhysicalDisk` + `Get-Disk` + `Get-Volume` + `Get-Partition` combined). `df -h` shows mounted volumes (like `Get-Volume`), `du -sh` shows directory sizes (like `Get-ChildItem -Recurse`), and `blkid` shows partition UUIDs/types (like `wmic volume list`). **Mount points replace drive letters** — every filesystem mounts to a directory (`/mnt/data`, `/home/user`), defined in `/etc/fstab` (persistent) or `mount` (temporary). **LVM** (`pvs`, `vgs`, `lvs`, `lvextend`, `resize2fs`) is Linux's equivalent to Windows Storage Spaces — it allows dynamic resizing without rebooting. **ZFS** offers more advanced pooling (RAID, snapshots, compression) but has a steeper learning curve. **`/etc/fstab`** is the persistent mount config (Windows: registry drive letter assignment). **USB drives** auto-mount in GUI; CLI equivalent is `udisksctl mount`. **Network shares** use `mount -t cifs` (SMB) or `mount -t nfs` (NFS). **No drive letter concept** — Linux mounts everything under directories, and `df -Th` shows all mounted filesystems with types.
