# Module 4: File Permissions

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage NTFS permissions and Share permissions:

```
NTFS Permissions:
  C:\Folder\
  ├── Full Control  (read, write, delete, change permissions)
  ├── Modify        (read, write, delete)
  ├── Read & Execute (read, execute)
  └── Traverse Folder (enter directory)

  Inheritance: permissions flow from parent to child
  ACEs: Access Control Entries (Allow/Deny, user/group specific)
  Security tab → Advanced → Add/Edit/Remove entries
```

Windows uses **discretionary access control (DAC)** with **Access Control Lists (ACLs)**. Each file has a Security Descriptor with a Discretionary ACL (DACL). Permissions are **Allow** or **Deny** for **users or groups**, with **inheritance** from parent folders.

## The Shift

Linux uses a **three-bit model** — Owner, Group, Others — each with **Read (4), Write (2), Execute (1)**. It's numeric, not a GUI list. No native inheritance — you use **default masks** and **setgid** bits instead.

```bash
# The permission string: what you see in ls -l
# d rwx r-x r--  .  file.txt
#   |---| |---| |---|
#   |   |   |    └── Others (everyone else)
#   |   |   └── Group
#   |   └── Owner (user)
#   └── File type (d=dir, -=file, l=symlink, b=block device, c=char device)

# The octal: the numbers behind it
# rwx = 4+2+1 = 7 (full)
# r-x = 4+0+1 = 5 (read + execute)
# r-- = 4+0+0 = 4 (read only)
# --- = 0 (no permissions)
```

### Side-by-Side: Permission Values

| Octal | rwx Breakdown | Meaning | NTFS Equivalent |
|------:|------|------|---------|
| 777 | rwx rwx rwx | Full to everyone | Full Control to Everyone |
| 755 | rwx r-x r-x | Owner full, others read+exec | Owner Modify, Others Read & Execute |
| 750 | rwx r-x --- | Owner full, group read+exec, others nothing | Owner Modify, Group Read & Execute |
| 644 | rw- r-- r-- | Owner read+write, others read | Owner Modify, Others Read |
| 600 | rw- --- --- | Owner read+write only | Owner Modify, no one else |
| 640 | rw- r-- r-- | Owner read+write, group read | Owner Modify, Group Read |
| 700 | rwx --- --- | Owner only | Owner Full Control, no one else |
| 666 | rw- rw- rw- | Read+write to everyone | Everyone Modify |
| 660 | rw- rw- --- | Read+write to owner + group | Owner + Group Modify |

### Octal Quick Math

```bash
# Each category adds: r=4, w=2, x=1
# 4+2+1 = 7 (rwx — full)
# 4+2+0 = 6 (rw- — read+write)
# 4+0+1 = 5 (r-x — read+execute)
# 4+0+0 = 4 (r-- — read only)
# 0+2+1 = 3 (-wx — write+execute)
# 0+2+0 = 2 (w-- — write only)
# 0+0+1 = 1 (–x — execute only)
# 0+0+0 = 0 (--- — no permissions)

# Examples:
# 755 = rwx (owner) + r-x (group) + r-x (others)
# 644 = rw- (owner) + r-- (group) + r-- (others)
# 4755 = setuid + rwxr-xr-x
# 1777 = sticky + rwxrwxrwx (/tmp has this)
```

### ls Output — Reading Permissions

```bash
# Full ls -l output (Windows: Get-Acl)
ls -la /etc/ssh/sshd_config

# Output: -rw-r----- 1 root sshd 3884 Jun 15 14:30 /etc/ssh/sshd_config
# Position: 123456789012
# 1: File type  (– = regular file)
# 2-4: Owner (rw- = read + write)
# 5-7: Group (r-- = read only)
# 8-10: Others (--- = nothing)
# 11: Owner name (root)
# 12: Group name (sshd)

# See full details (Windows: Get-Acl file | Format-List)
ls -lad /etc /tmp /var/log

# Example output:
# drwxr-xr-x  141 root root  12288 Jun 15 10:00 /etc     (dir, full owner, others read+exec)
# drwxrwxrwt    7 root root   4096 Jun 15 10:00 /tmp     (sticky bit!)
# drwxr-xr-x    2 root root   4096 Jun 15 10:00 /var/log
```

### chmod — Change Permissions

```bash
# Octal notation (Windows: icacls /grant)
chmod 755 /usr/local/bin/script.sh    # rwx r-x r-x
chmod 644 /var/www/index.html          # rw- r-- r--
chmod 600 ~/.ssh/authorized_keys       # rw- --- --- (secret key!)
chmod 700 ~/.ssh                       # rwx --- --- (private dir)

# Symbolic notation (Windows: icacls file /grant user:RX)
chmod u+x script.sh                     # Add execute for owner
chmod g+w config.yml                    # Add write for group
chmod o-rwx database.conf               # Remove all for others
chmod a+r public-notes.txt              # Add read for all (u+g+o)
chmod u=rw,g=r,o= file.txt              # Owner rw, group read, none for others
chmod u+s binary                        # Set UID bit
chmod g+s /shared/project                # Set GID bit
chmod +t /shared/public                  # Sticky bit

# Recursively change permissions (Windows: icacls /t /c)
chmod -R 644 /var/www/html              # All files in dir
chmod -R 755 /var/www/html              # All dirs in dir
find /var/www/html -type f -exec chmod 644 {} \;   # Files only, 644
find /var/www/html -type d -exec chmod 755 {} \;   # Dirs only, 755
```

### chown — Change Owner

```bash
# Change file owner (Windows: icacls /setowner)
sudo chown david:staff /home/david/docs        # owner:group
sudo chown david /home/david/docs               # just owner
sudo chown :devops /home/david/docs             # just group

# Recursive chown (Windows: takeown /f * /r)
sudo chown -R www-data:www-data /var/www/html
sudo chown -R $USER:$USER /home/$USER/projects

# Change group only
chgrp developers /shared/project
```

### Default Permissions — umask

```bash
# umask = what to SUBTRACT from 777 (Windows has no direct equivalent)
# New files get: 666 - umask = permissions
# New dirs get: 777 - umask = permissions

umask                        # Show current umask (usually 022)
umask 022                    # Set umask (default on most systems)

# How umask works:
# umask 022 → files = 666-022 = 644, dirs = 777-022 = 755
# umask 002 → files = 666-002 = 664, dirs = 777-002 = 775
# umask 077 → files = 666-077 = 600, dirs = 777-077 = 700

# Make umask persistent (Windows: registry GPO)
echo "umask 022" >> ~/.bashrc
```

### The Special Bits

```bash
# Three special permission bits beyond rwxrwxrwx:

# 1. SUID (Set Owner UID) — run file as file's owner
chmod 4755 /usr/bin/passwd
# When executed, runs as root (not as the user who ran it)
# Windows equivalent: run as administrator

# 2. SGID (Set Group ID) — new files inherit parent's group
chmod 2755 /shared/project
# New files in this dir get the group, not the creator's primary group
# Like Windows folder inheritance for permissions

# 3. Sticky Bit — only owner can delete their own files
chmod 1777 /shared/public
# /tmp uses this: anyone can write, but only the creator can delete
# Windows equivalent: Everyone has Write but only Owner can Delete

# See them in ls output:
ls -ld /tmp                    # drwxrwxrwt (the 't' = sticky)
ls -ld /usr/bin/passwd         # -rwsr-xr-x (the 's' = SUID/SGID)
ls -ld /usr/bin/sudo           # -rwsr-x--- (SUID — runs as root)
```

### Windows NTFS → Linux Permission Mapping

| NTFS Concept | Linux Equivalent | Notes |
|------|--------|-------|
| Full Control | 777 / 755 (on dirs) | Not one-to-one — more granular |
| Read & Execute | 755 (dirs) / 644 (files) | Standard web file permission |
| Modify | 664 (files) / 775 (dirs) | Owner+group read+write |
| Read Only | 644 | Owner writes, everyone reads |
| No Access | 000 | Hide the file entirely |
| Inheritance | setgid bit + default ACLs | NTFS inheritance doesn't exist natively |
| Deny ACE | Can't combine with allow | Linux has no Deny bit — absence of perms IS the deny |
| Owner | First octal (rwx) | Only 1 owner, not multiple |
| Multiple groups | Secondary groups | User can belong to many groups |
| Everyone | Others (last octal) | All unprivileged users |
| SYSTEM / TrustedInstaller | root | root can do anything |
| Administrators | sudo / root | Sudoers list in /etc/sudoers |

### Groups — The Multi-Group Model

```bash
# Users can belong to multiple groups (unlike Windows primary + secondary)
id                           # Show your groups
groups                       # Just your group list
cat /etc/group               # All groups on the system
getent group sudo            # Members of sudo group
getent group www-data        # Members of www-data group

# Add yourself to a group (Windows: Active Directory group membership)
sudo usermod -aG docker $USER    # Add to docker group
sudo usermod -aG devops $USER    # Add to devops group
# IMPORTANT: log out and back in for group changes to take effect!

# Create a group (Windows: New-LocalGroup)
sudo groupdevs developers
sudo gpasswd -a david developers

# Set group of a file (Windows: icacls /setowner)
chgrp developers /shared/project
```

### ACLs — Fine-Grained Control (When You Need It)

```bash
# Linux has ACLs for when rwx isn't enough (Windows has ACLs natively)
# Install: sudo apt install acl

# Set ACL for a specific user (Windows: icacls file /grant user:RX)
setfacl -m u:david:rw /shared/project/file.txt
setfacl -m u:david:r-x /shared/project

# Get ACL (Windows: icacls file)
getfacl /shared/project/file.txt

# Copy ACLs (Windows: icacls /save)
getfacl -R /shared/project > project-acl.txt
setfacl -R -M project-acl.txt /shared/project

# Set default ACL for new files (like NTFS inheritance)
setfacl -d -m u:david:rwx /shared/project
setfacl -d -m u:webuser:r-x /shared/project
# New files created here inherit these defaults!

# Remove ACL (Windows: icacls /remove)
setfacl -x u:david /shared/project/file.txt    # Remove one entry
setfacl -b /shared/project/file.txt             # Remove all ACLs
```

### Permission Checking Order

```bash
# How Linux checks permissions (order matters!):
# 1. Does the user own the file? → Owner permissions apply
# 2. Is the user in the file's group? → Group permissions apply
# 3. Nothing matches → Others permissions apply
# 4. root/sudo can bypass all of the above

# Example: file owned by root:developers with perms 640
# root → 6 (rw-)
# david (in developers group) → 4 (r--)
# bob (not in developers group) → 0 (---)

# Directory traversal: you need execute (x) on directories to enter them
# This is why you can't just chmod 644 a directory — you need 755
ls -ld /var/log/nginx
# drwxr-xr-x means: owner can enter, group can enter, others can enter
# If it were drw-r----- → nobody except root can enter that directory!
```

## Hands-On Exercise

```bash
# 1. Check current permissions
ls -la ~/.ssh/
ls -la /etc/ssh/sshd_config

# 2. Create a test directory and set permissions
mkdir -p /tmp/lab/permissions/{public,private,shared}
chmod 755 /tmp/lab/permissions/public
chmod 700 /tmp/lab/permissions/private
chmod 2770 /tmp/lab/permissions/shared

# 3. Create files and check their permissions
touch /tmp/lab/permissions/public/readme.txt
touch /tmp/lab/permissions/shared/data.csv
chmod 664 /tmp/lab/permissions/shared/data.csv
ls -la /tmp/lab/permissions/public/
ls -la /tmp/lab/permissions/shared/

# 4. Check umask
umask
touch /tmp/lab/test-default.txt
ls -la /tmp/lab/test-default.txt  # Should be 644 if umask is 022

# 5. Change file ownership
sudo chown $USER:$USER /tmp/lab/permissions/shared/data.csv
ls -la /tmp/lab/permissions/shared/data.csv

# 6. Use ACLs (if installed)
setfacl -m u:$USER:rwx /tmp/lab/permissions/shared
getfacl /tmp/lab/permissions/shared

# 7. Fix common permission issues
chmod 600 ~/.ssh/authorized_keys    # SSH key should be secret!
chmod 700 ~/.ssh                    # SSH dir should be secret!

# 8. Find world-writable files (security audit)
find / -perm -o+w -type f 2>/dev/null | head -20
```

## Mental Model Shift

| Windows NTFS Mindset | Linux Permission Mindset |
|-------------|------|---|
| GUI Security tab → ACE list | `ls -l` → octal string (755, 644, etc.) |
| Multiple owners via ACLs | One owner, one group per file |
| Inheritance flows down tree | setgid + default ACLs for inheritance |
| Allow / Deny entries | Absence of permission = Deny (no Deny bit!) |
| icacls (text) / Security tab (GUI) | chmod, chown, getfacl, setfacl (text only) |
| Administrators group = elevated | sudo = elevated (explicit whitelist) |
| Everyone inherits parent permissions | New files get umask-based permissions |
| Full Control = everything | 777 = everything (rarely appropriate) |
| Take ownership via GUI or takeown.exe | chown (requires root) |
| `*` = grant all perms to user | chmod 755/777 — pick the right subset |

**Key takeaway:** Linux permissions are **numeric** and **compact** (755, 644, 600). The three categories — Owner, Group, Others — map to Owner, your groups, and everyone else. There's no Deny bit; absence of a permission IS the deny. Use `chmod` (numbers), `chown` (ownership), and `umask` (defaults). When you need NTFS-like granularity, use ACLs (`setfacl` / `getfacl`). Most Windows admins struggle with "why can't I read this?" — check both the file permissions AND the directory permissions (need x on every parent directory to reach a file).
