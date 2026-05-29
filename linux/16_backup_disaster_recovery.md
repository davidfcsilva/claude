# Module 16: Backup & Disaster Recovery

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage backups and disaster recovery through:

```
Windows:
  wbadmin start backup → System/Full backup
  wbadmin get versions → List backup versions
  wbadmin recover → Restore from backup
  VSS (vssadmin) → Volume Shadow Copy Service
  vssadmin list shadow → List shadow copies
  vssadmin delete shadows → Delete shadow copies
  Get-Volume | Get-WmiObject -Class Win32_ShadowCopy → List shadows
  New-PSDrive -Name back -PSProvider FileSystem -Root \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\ → Access shadow copy
  Get-ChildItem \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\ → Browse shadow files
  robocopy C:\ D:\backup /MIR /Z → File-level backup
  xcopy /D → Incremental backup (date-based)
  Get-BCTask → Backup task status
  Get-ScheduledTask → Scheduled backup tasks
  Backup-VM → Hyper-V VM backup
  Export-VMPulse → VM export for disaster recovery
  Get-WindowsOptionalFeature → OS component state
  DISM /Export-WindowsImage → OS image backup
  System State backup → Registry + boot files + AD database
  Recover-Computer → Domain recovery
  dcdiag → AD health check (recovery verification)
  Get-Command -Module Storage → Storage-related cmdlets
  Get-Command -Module VSS → Volume Shadow Copy cmdlets
```

Windows backup centers on **Shadow Copy/VSS** (instant point-in-time snapshots), **wbadmin** (system-level backup/restore), **robocopy** (file-level replication), and **scheduled task-based backup jobs**.

## The Shift

Linux backups use a **toolkit approach** — each tool handles a different layer: **rsync** for file synchronization, **tar** for archives, **dump/restore** for filesystem-level, **borg** for deduplicated encrypted backups, **LVM snapshots** for instant point-in-time copies, and **dd** for disk imaging. Unlike Windows' integrated Shadow Copy system, Linux has **no unified snapshot API** — you layer tools for the same outcome. **rsync over robocopy** is the key shift: rsync is faster, supports delta transfers, SSH tunneling, and exclusion patterns. **No single "Windows Backup" equivalent** — you compose your own backup pipeline. **Incremental/differential backups** are native to rsync and borg (not date-based like robocopy's /D). **LVM snapshots** replace VSS for block-level point-in-time copies. **Cron + scripts** replace Scheduled Tasks for automation.

---

## rsync — File Synchronization

### Local & Remote Sync

```bash
# Local sync (Windows: robocopy /MIR or xcopy)
rsync -av /source/ /destination/           # Mirror directory (Windows: robocopy C:\src D:\dst /MIR)
rsync -avz user@remote:/path /local/       # Pull from remote (Windows: robocopy \\\\remote\\share C:\\dst /MIR)
rsync -avz /local/ user@remote:/path/      # Push to remote (Windows: robocopy C:\\src \\\\remote\\share /MIR)
rsync -av --delete /source/ /destination/  # Delete files in dest not in source (MIR behavior)
rsync -avz --delete user@remote:/path/ /local/  # Remote sync with deletion

# Incremental sync (Windows: robocopy /MIR /IS /IT — rsync does this by default!)
rsync -av --checksum /source/ /dest/       # Use checksum instead of mtime/size
rsync -av --bwlimit=1000 /source/ /dest/   # Bandwidth limit (KB/s)
rsync -av --partial --progress /source/ /dest/  # Show progress, keep partial files

# Remote sync with SSH (Windows: robocopy with mapped network drive)
rsync -avz -e ssh /source/ user@host:/dest/  # SSH tunnel (Windows: map \\host\share)
rsync -avz -e "ssh -i ~/.ssh/key" /source/ user@host:/dest/  # SSH key

# Exclude patterns (Windows: robocopy /XF /XD)
rsync -av --exclude='*.log' --exclude='tmp/' /source/ /dest/
rsync -av --exclude-from='exclude.txt' /source/ /dest/  # From file
rsync -av --include='*.txt' --exclude='*' /source/ /dest/  # Include only txt files
```

### rsync as Daemon (Module)

```bash
# rsync server (Windows: network share via SMB)
# /etc/rsyncd.conf:
# [backups]
#   path = /data/backups
#   read only = no
#   uid = root
#   gid = root
#   hosts allow = 192.168.1.0/24

rsync -av /source/ rsync://host/backups/   # Pull from rsync module
rsync -av rsync://host/backups/ /dest/     # Push to rsync module
```

### Key rsync Flags

```bash
rsync -avzP /source/ /dest/                # archive, verbose, compress, show progress
rsync -a                                   # Archive mode (-rlptgoD)
rsync -v                                   # Verbose
rsync -z                                   # Compress data
rsync -P                                   # Progress (same as --partial --progress)
rsync --delete                             # Delete extraneous files from dest
rsync --dry-run                            # Preview what would happen
rsync --itemize-changes                  # Show detailed changes
```

---

## tar — Archive Compression

### Create & Extract Archives

```bash
# Create archives (Windows: 7z / PowerShell Compress-Archive)
tar -czvf backup.tar.gz /source/           # Compress with gzip (Windows: 7z a -tgzip backup.7z source)
tar -cjvf backup.tar.bz2 /source/          # Compress with bzip2
tar -cJvf backup.tar.xz /source/           # Compress with xz (best compression)
tar -czvf - /source/ | ssh user@host "tar -xzvf - -C /dest/"  # Stream to remote

# Extract archives (Windows: 7z x)
tar -xzvf backup.tar.gz                    # Extract gzip (Windows: 7z x backup.7z)
tar -xjvf backup.tar.bz2                   # Extract bzip2
tar -xJvf backup.tar.xz                    # Extract xz
tar -xzvf backup.tar.gz -C /dest/          # Extract to specific directory

# List contents (Windows: 7z l)
tar -tzvf backup.tar.gz                    # List files
tar -tzvf backup.tar.gz | grep pattern     # Search within archive

# Append to archive (Windows: 7z u)
tar -rvf backup.tar file1 file2            # Append files (uncompressed only)
```

---

## dump/restore — Filesystem-Level Backup

```bash
# dump/restore (Windows: wbadmin, VSS)
sudo apt install dump                      # Install dump tool
sudo dump -0auL -f /backup/full.dump /     # Full backup of / filesystem
sudo dump -1auL -f /backup/inc1.dump /     # Incremental backup (level 1)
sudo dump -2auL -f /backup/inc2.dump /     # Incremental backup (level 2)
sudo restore -if /backup/full.dump          # List dump contents
sudo restore -rif /backup/full.dump        # Restore entire dump
sudo restore -xif /backup/full.dump -s /extracted/  # Restore selectively
```

---

## LVM Snapshots — Point-in-Time Backups

```bash
# LVM snapshots (Windows: vssadmin list shadows / New-VolumeShadowCopy)
# Prerequisites: /dev/vg0/data is a logical volume

# Create a snapshot (instant, minimal space)
sudo lvcreate -L 1G -s -n data-snap /dev/vg0/data  # Create 1GB snapshot
sudo mount /dev/vg0/data-snap /mnt/snap            # Mount for backup
rsync -av /mnt/snap/ /backup/data/                 # Backup from snapshot
sudo umount /mnt/snap                              # Cleanup
sudo lvremove /dev/vg0/data-snap                   # Remove snapshot

# Automated snapshot + backup (Windows: ScheduledTask + wbadmin)
# /etc/crontab or /etc/systemd/system/backup-snapshot.timer:
# 0 2 * * * /usr/local/bin/backup.sh               # Daily at 2 AM

# backup.sh:
#!/bin/bash
SNAP="snap-$(date +%Y%m%d)"
lvcreate -L 500M -s -n $SNAP /dev/vg0/data
mount /dev/vg0/$SNAP /mnt/snap
rsync -av --delete /mnt/snap/ /backup/data-$(date +%Y%m%d)/
umount /mnt/snap
lvremove -f /dev/vg0/$SNAP
```

---

## borg — Deduplicated Encrypted Backups

```bash
# Borg (Windows: no direct equivalent; most similar: robocopy + backup software like Macrium)
sudo apt install borgbackup                        # Install borg
borg init --encryption=repo-key /backup/borg-repo  # Initialize repo
borg create /backup/borg-repo::backup-{now} /home  # Create backup (auto-deduplicated!)
borg list /backup/borg-repo                        # List archives
borg list /backup/borg-repo::backup-20240101       # List files in specific archive
borg extract /backup/borg-repo::backup-20240101    # Extract all files
borg extract /backup/borg-repo::backup-20240101:path/to/file  # Extract specific file
borg prune /backup/borg-repo --keep-daily=7 --keep-weekly=4 --keep-monthly=6  # Retention policy
borg compact /backup/borg-repo                     # Reclaim space
borg info /backup/borg-repo::backup-20240101       # Archive info
borg check /backup/borg-repo                       # Verify integrity
```

---

## dd — Disk Imaging

```bash
# dd disk imaging (Windows: Rufus disk imaging, Clonezilla, Macrium Reflect)
sudo dd if=/dev/sda of=/backup/sda.img bs=4M status=progress  # Full disk backup
sudo dd if=/dev/sda1 of=/backup/sda1.img bs=4M status=progress  # Partition backup
sudo dd if=/backup/sda.img of=/dev/sda bs=4M status=progress  # Restore disk

# Compressed disk imaging (Windows: Macrium Reflect compress)
sudo dd if=/dev/sda | gzip -c > /backup/sda.img.gz  # Compress backup
gzip -dc /backup/sda.img.gz | sudo dd of=/dev/sda   # Compress restore
```

---

## restic — Modern Deduplicated Backup

```bash
# restic (Windows: no direct equivalent; similar to borg)
sudo apt install restic                            # Install restic
restic init --repo /backup/restic                  # Initialize repository
restic backup /home /etc                           # Backup multiple paths
restic ls /backup/restic                           # List backups
restic ls --tree /backup/restic/latest/home        # Browse files
restic restore latest -t /restore/                 # Restore latest backup
restic forget --keep-daily=7 --keep-weekly=4 /backup/restic  # Prune
restic prune /backup/restic                        # Clean up
restic stats /backup/restic                        # Repository stats
restic snapshots /backup/restic                    # List all snapshots
restic backup --exclude '*.log' --exclude 'tmp/' /home  # Excluded paths
```

---

## Backup Automation & Scheduling

```bash
# Cron (Windows: Scheduled Tasks / schtasks.exe)
crontab -e                                         # Edit cron jobs
0 2 * * * /usr/local/bin/backup-home.sh            # Daily at 2 AM
0 */6 * * * /usr/local/bin/backup-configs.sh       # Every 6 hours
0 3 * * 0 /usr/local/bin/backup-weekly.sh          # Sundays at 3 AM
@daily /usr/local/bin/backup-daily.sh              # Daily shortcut
@hourly /usr/local/bin/backup-hourly.sh            # Hourly shortcut

# Systemd timer (Windows: Scheduled Tasks alternative)
# /etc/systemd/system/backup.timer:
# [Unit]
# Description=Daily Backup Timer
#
# [Timer]
# OnCalendar=*-*-* 02:00:00
# RandomizedDelaySec=300
# Persistent=true
#
# [Install]
# WantedBy=timers.target

# /etc/systemd/system/backup.service:
# [Unit]
# Description=Daily Backup Service
#
# [Service]
# Type=oneshot
# ExecStart=/usr/local/bin/backup.sh

systemctl enable --now backup.timer                # Enable timer
systemctl status backup.timer                      # Check timer status
systemctl list-timers                              # List all timers
```

---

## Disaster Recovery Patterns

```bash
# 3-2-1 Backup Rule (Windows: same concept, different tools)
# 3 copies of data (original + 2 backups)
# 2 different media types (local disk + cloud/tape/remote)
# 1 offsite copy (remote/cloud)

# Local backup (Windows: external drive / network share)
rsync -avz /home/ /backup/home/                    # Local backup
borg create /backup/borg::local-{now} /home        # Deduplicated local

# Remote backup (Windows: robocopy to network share)
rsync -avz /backup/ user@remote-host:/remote-backup/  # Remote sync
restic backup --repo s3:s3.amazonaws.com/bucket /home  # Cloud backup (S3)
restic backup --repo azure:container /home         # Cloud backup (Azure)
borg create /backup/borg::offsite-{now} /home      # Deduplicated offsite

# Disaster Recovery (Windows: System State recovery, wbadmin recover)
# Bare metal recovery:
# 1. Boot from recovery media (Ubuntu Live USB)
# 2. Connect to backup source
# 3. Restore system files and data

# System state recovery (Windows: wbadmin recover -systemstate)
# Reinstall OS → restore configs → restore data

# Bootable recovery (Windows: Windows Installation Media / Recovery Disk)
# Create recovery media:
# - Ubuntu Live USB (universal)
# - SystemRescue CD (specialized)
# - Clonezilla (disk imaging)

# Verify backup integrity (Windows: wbadmin get itemsrecoverystatus)
borg check /backup/borg-repo                       # Borg integrity check
restic check --read-data /backup/restic            # Restic integrity check
rsync -av --checksum /source/ /dest/               # Verify with checksum comparison
```

---

## Hands-On Exercise

```bash
# 1. File-level backup with rsync
mkdir -p /backup/test
rsync -avz /home/$USER/ /backup/test/home/
rsync -av --delete --dry-run /backup/test/home/ /verify/home/  # Verify

# 2. Archive with tar
tar -czvf /backup/home-$(date +%Y%m%d).tar.gz /home/$USER/.config

# 3. Borg deduplicated backup
borg init --encryption=repo-key /backup/borg
borg create /backup/borg::first-{now} /home/$USER/.config
borg create /backup/borg::second-{now} /home/$USER/.config  # Only changes stored!
borg list /backup/borg

# 4. Automate with cron
crontab -e
# Add: 0 3 * * * /usr/local/bin/borg-backup.sh
```

---

## Mental Model Shift

| Windows Backup & Disaster Recovery | Linux Backup & Disaster Recovery |
|---|---|
| Shadow Copy/VSS → Volume Shadow Copy Service | LVM snapshot → block-level instant copy (lvcreate -s) |
| wbadmin start backup → system backup | dump -0auL → full filesystem backup |
| wbadmin recover → restore from backup | dump/restore → restore filesystem |
| vssadmin list shadow → view snapshots | lvdisplay → view LVM snapshots |
| robocopy C:\ D:\ /MIR → mirror sync | rsync -av --delete → mirror sync |
| robocopy \\\\remote\\share → network copy | rsync -avz -e ssh user@host:/path → encrypted copy |
| robocopy /XF /XD → exclude files/folders | rsync --exclude/--exclude-from → exclude patterns |
| robocopy /Z → resumable copy | rsync --partial → resumable with progress |
| robocopy /MIR → full mirror | rsync -a → archive mode (preserves permissions/links) |
| Windows Backup GUI → wizard-driven backups | CLI pipeline → composible scripts |
| Scheduled Task → backup schedule | crontab → same scheduling concept |
| Get-ScheduledTask → view scheduled backups | crontab -l / systemctl list-timers |
| Macrium Reflect → disk imaging | Clonezilla / dd → disk imaging |
| diskpart → manage volumes | lvm/pvcreate/vgcreate/lvcreate → manage volumes |
| System State backup → AD+registry+boot | dump + tar → system file backup |
| Get-WindowsImage → OS image | dd / DISM → OS imaging |
| Recover-Computer → domain recovery | restore configs + rejoin domain |
| dcdiag → AD health check | borg check → backup integrity |
| Shadow Copy → per-volume snapshots | LVM → lvcreate -s for per-volume snapshots |
| Windows → SMB network shares | Linux → rsync over SSH / S3 / Azure |
| Windows → built-in encryption in GUI | Linux → borg/restic built-in encryption (CLI) |
| Windows → backup version retention in GUI | Linux → borg prune → retention policy |
| Windows → backup history in event viewer | Linux → borg list + cron log → backup history |
| Windows → Recovery Drive / System Repair | Linux → Ubuntu Live USB / SystemRescue CD |
| Windows → WIM images (DISM) | Linux → dd raw images (gzip/zstd compressed) |
| Windows → OneDrive as sync | Linux → rclone as universal cloud sync |
| Windows → Storage Spaces → RAID, not backup | Linux → LVM RAID → mirrored storage, not backup |
| Windows → single vendor solution (Microsoft) | Linux → best-of-breed toolkit |
| Windows → automatic backup alerts | Linux → cron logs + monitoring → manual/alert-based |
| Windows → Volume Shadow Copy → per-volume | Linux → LVM snapshot → per-volume (no FS-wide) |
| Windows → wbadmin → full system backup | Linux → tar + rsync → granular restore |
| Windows → Disk Management → VHD/VHDX | Linux → dd → disk-to-image (raw) |
| Windows → System Image Recovery | Linux → dd restore + reinstall → bare metal recovery |
| Windows → backup encryption via DPAPI | Linux → borg → AES-256 encryption |
| Windows → backup dedup (Deduplication feature) | Linux → borg → automatic deduplication |
| Windows → Backup and Restore (legacy) | Linux → multiple tools → each specialized |

**Key takeaway:** Linux has no single "Windows Backup" equivalent — you compose your own backup pipeline. **rsync** is your daily driver for file sync (replaces robocopy, but better with delta transfers and SSH). **tar** is for archives (like 7z). **borg/restic** provide deduplicated encrypted backups (Windows has no native equivalent). **LVM snapshots** give you instant point-in-time copies (like VSS). **dd** handles disk imaging. **cron/systemd timers** automate everything (like Scheduled Tasks). The **3-2-1 rule** (3 copies, 2 media, 1 offsite) applies the same — just build it from tools instead of one GUI.
