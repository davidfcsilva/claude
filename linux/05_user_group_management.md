# Module 5: User & Group Management

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage users and groups through:

```
Active Directory:
  - New-ADUser, New-ADGroup
  - AD Users and Computers (dsa.msc)
  - Users → Domain Users, Domain Admins, etc.
  - Password policy via GPO
  - Users are objects with properties (sAMAccountName, givenName, etc.)

Local Computer:
  - lusrmgr.msc (Local Users and Groups)
  - net user /add (CMD)
  - net localgroup /add
  - Users, Administrators, Guests, Guests, Power Users
```

Windows separates **domain** and **local** accounts. Domain accounts are managed centrally via Group Policy.

## The Shift

Linux has **no centralized user store by default**. Users live in `/etc/passwd` and `/etc/shadow`. There's no "Domain Users" group — you use **system users** and **service accounts** managed locally (or LDAP/SSSD for enterprise).

```bash
# The core files (Windows: SAM database + Active Directory)
/etc/passwd       # User list (readable by everyone)
/etc/shadow       # Password hashes (root only)
/etc/group        # Group memberships
/etc/gshadow      # Group passwords (root only)
```

### The Core Files

```bash
# /etc/passwd — user database (Windows: SAM database)
cat /etc/passwd | head -5

# Format: username:password_placeholder:UID:GID:GECOS:home:shell
# Example output:
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash
mysql:x:1001:1001::/nonexistent:/usr/sbin/nologin

# Fields:
#   1: Username
#   2: Password (x = hash in /etc/shadow)
#   3: UID (user ID — 0 = root!)
#   4: GID (primary group ID)
#   5: GECOS (comment/full name)
#   6: Home directory
#   7: Login shell

# /etc/shadow — password hashes (Windows: SAM encrypted hashes)
sudo cat /etc/shadow
# Format: username:password_hash:last_changed:min_age:max_age:warn:inactive:expire

# /etc/group — group memberships (Windows: group membership table)
cat /etc/group | head -10
# Format: group_name:password_placeholder:GID:user_list
# Example: sudo:x:27:ubuntu,david
#           ^     ^  ^    ^^^^^^^^^^^^^^
#           name  p  gid   members (comma separated)
```

### Creating & Managing Users

```bash
# Create a user (Windows: New-ADUser / net user /add)
sudo adduser david          # Interactive — creates home, sets password (Debian/Ubuntu)
sudo useradd -m -s /bin/bash david  # Non-interactive (RHEL/CentOS style)
sudo useradd -m -s /bin/bash -c "David Silva" david  # With full name

# Set password (Windows: Set-ADAccountPassword)
sudo passwd david
sudo passwd david           # Interactive password prompt
echo "david:newpassword" | sudo chpasswd   # Non-interactive (not recommended in scripts)

# Delete a user (Windows: Remove-ADUser / net user /delete)
sudo deluser david          # Debian/Ubuntu (removes home)
sudo userdel david           # Standard (use -r to remove home)
sudo userdel -r david        # Also remove home directory and mail spool

# Modify user (Windows: Set-ADUser)
sudo usermod -aG docker,david          # Add to groups
sudo usermod -s /bin/zsh david         # Change shell
sudo usermod -L david                  # Lock account (disable)
sudo usermod -U david                  # Unlock account
sudo usermod -c "David Silva" david    # Change GECOS (full name)
```

### Managing Groups

```bash
# Create a group (Windows: New-ADGroup / net localgroup /add)
sudo groupadd developers
sudo groupadd devops

# List groups (Windows: Get-LocalGroup)
getent group | head -20
cat /etc/group

# Add users to a group (Windows: Add-ADGroupMember)
sudo usermod -aG developers david
sudo gpasswd -a david developers
sudo gpasswd -a david devops

# Remove from group (Windows: Remove-ADGroupMember)
sudo gpasswd -d david developers
sudo deluser david developers

# List group members (Windows: Get-ADGroupMember)
getent group developers
sudo groupmems -g developers -l

# Delete a group
sudo groupdel developers
```

### User Types

```bash
# Users on your system (Windows: Get-LocalUser)
cat /etc/passwd | cut -d: -f1
getent passwd | grep -v nologin | grep -v false    # Users who can login

# System users vs real users (Windows: built-in vs domain users)
# System users (UID < 1000) — for services
# Real users (UID >= 1000) — humans

# Common system users:
root          # UID 0 — the superuser (Windows: Administrator)
daemon        # UID 1 — legacy system processes
nobody        # UID 65534 — unprivileged process user
www-data      # Web server user (Ubuntu/Debian)
apache        # Web server user (RHEL/CentOS)
mysql         # MySQL database user
nginx         # Nginx web server user
postgres      # PostgreSQL database user
dbus          # D-Bus message bus
sshd          # SSH daemon

# Check if a user can login (Windows: Get-ADUser | Select-Object Enabled)
grep david /etc/passwd | grep -v nologin | grep -v false    # Can login
grep david /etc/passwd | grep nologin                        # Cannot login
```

### Sudo — Privilege Escalation

```bash
# Sudo configuration (Windows: RunAs, Administrators group)
sudo whoami          # Run as root
sudo -u www-data ls /var/www    # Run as specific user
sudo -l                  # List current user's sudo privileges
sudo visudo              # Edit /etc/sudoers safely (syntax check!)

# /etc/sudoers format (Windows: local Administrators group)
# username  ALL=(ALL) ALL            # Full sudo access
# username ALL=(ALL) NOPASSWD:ALL    # Full sudo, no password
# username ALL=(ALL) /usr/bin/apt    # Only allowed to run apt
# %sudo ALL=(ALL) ALL                # All users in sudo group can sudo
# %admin ALL=(ALL) ALL               # All users in admin group can sudo
# root    ALL=(ALL) ALL              # Root can do anything

# Default: in Ubuntu, members of the 'sudo' group can sudo
# In RHEL, members of the 'wheel' group can sudo
groups                         # Check your groups
sudo cat /etc/shadow           # Run as root to read shadow
```

### Key Management & Password Policy

```bash
# Password aging (Windows: net accounts /maxpwage /minpwage)
chage -l david                   # Show password aging info
chage -M 90 david                # Password expires every 90 days
chage -m 7 david                 # Minimum 7 days between password changes
chage -W 14 david                # Warn 14 days before expiry
chage -E 2026-12-31 david        # Account expires on date
chage -d 0 david                 # Force password change on next login

# Lock/unlock accounts (Windows: Disable-ADAccount)
sudo passwd -l david             # Lock
sudo passwd -u david             # Unlock
sudo usermod -L david            # Lock (alternative)
sudo usermod -U david            # Unlock (alternative)

# Set account expiry (Windows: Account expires field in AD)
sudo usermod -e 2026-12-31 david

# Force password change on next login (Windows: "User must change password at next logon")
sudo chage -d 0 david

# Root — the superuser
su -                            # Switch to root (superuser)
su - david                      # Switch to david as root
sudo -i                         # Interactive root shell
sudo -s                         # Root shell with root's environment
```

### User Properties & Home Directory

```bash
# User info (Windows: Get-LocalUser / Get-ADUser)
id david                         # UID, GID, groups
whoami                           # Current username
whoami -u                        # UID
groups                           # Your groups
finger david                     # Full user info (requires finger package)
getent passwd david              # Get specific user entry
getent group sudo                # Get specific group entry

# Home directory (Windows: %USERPROFILE%)
echo $HOME                       # Your home directory
ls -la ~                         # Your home contents
getent passwd david | cut -d: -f6  # Get david's home directory
ls -la /home/david               # His home directory

# Copy home directory (Windows: copy profile)
sudo useradd -m -s /bin/bash -k /etc/skel -c "New User" newuser

# Skeleton files (Windows: Default Profile template)
ls -la /etc/skel/               # Files copied to new users' home
# Usually: .bashrc, .bash_profile, .profile
```

### Authentication & Login

```bash
# Who's logged in? (Windows: qwinsta, Get-WmiObject Win32_LogonSession)
who                              # Current logins
w                                # Current logins with details
last                             # Recent logins
lastb                            # Failed login attempts
lastlog                          # Last login for each user

# Check authentication status
loginctl list-sessions           # Active sessions (systemd)
loginctl show-session $(loginctl | grep $USER | awk '{print $1}')

# PAM — Pluggable Authentication Modules (Windows: Local Security Policy)
# Configuration in /etc/pam.d/ — controls password policy, login rules, etc.
cat /etc/pam.d/common-auth       # Authentication config
cat /etc/pam.d/common-account    # Account policy
cat /etc/pam.d/common-password   # Password policy
```

### Common UID/GID Ranges

```bash
# Standard UID ranges (Windows: SID ranges)
0          root (superuser)
1-999      System/reserved accounts
1000+      Real human users (starting UID)
65534      nobody (unprivileged)

# Standard GID ranges
0          root group
1          daemon
27         sudo
29         www-data
100        users
1000+      User-created groups (matching first user's UID)
```

## Hands-On Exercise

```bash
# 1. Explore user files
cat /etc/passwd | cut -d: -f1,6,7
cat /etc/group | grep sudo
cat /etc/group | grep developers

# 2. Create a test user
sudo adduser testuser
sudo passwd testuser
id testuser
getent passwd testuser

# 3. Add to groups
sudo usermod -aG sudo,david testuser
groups testuser

# 4. Set password aging
chage -M 90 testuser
chage -l testuser

# 5. Create a group
sudo groupadd developers
sudo gpasswd -a testuser developers
sudo groupmems -g developers -l

# 6. Check login status
who
w
last | head -10

# 7. Test sudo
sudo -l
sudo whoami

# 8. Lock and unlock the test user
sudo passwd -l testuser
sudo passwd -u testuser
sudo passwd -d testuser    # Delete password (for SSH key-only access)

# 9. Clean up
sudo deluser -r testuser
sudo groupdel developers
```

## Mental Model Shift

| Windows AD/Local Mindset | Linux User/Group Mindset |
|------|-------|-|
| AD Users and Computers GUI | `/etc/passwd` — plain text file |
| SAM database (encrypted) | `/etc/shadow` — password hashes (root only) |
| Get-ADUser | `getent passwd username` |
| Get-ADGroupMember | `getent group groupname` |
| New-ADUser / Add-LocalUser | `adduser` or `useradd` |
| Remove-ADUser | `deluser` or `userdel` |
| Add-ADGroupMember | `usermod -aG` or `gpasswd -a` |
| Disable-ADAccount | `passwd -l` or `usermod -L` |
| Enable-ADAccount | `passwd -u` or `usermod -U` |
| Set-ADAccountPassword | `passwd username` |
| User must change password at next logon | `chage -d 0` |
| Password policy (GPO) | `/etc/pam.d/common-password` + `chage` |
| Domain Users / Domain Admins | `sudo` group (or `wheel` on RHEL) |
| RunAs / Administrator group | `sudo` (explicit whitelist in `/etc/sudoers`) |
| Local Users and Groups (lusrmgr.msc) | No GUI — all CLI, files are plain text |
| Everyone inherits parent group | Users pick which groups to join |
| NoDeny bit → noDeny | |
| GPO password aging | `chage -M -maxDays`, `-m -minDays` |
| Account expires field | `usermod -e 2026-12-31` |
| System account (NetworkService) | System users with nologin shells |
| nologin users can't login | /usr/sbin/nologin (service accounts) |
| Home folder = %USERPROFILE% | /home/username |

**Key takeaway:** Linux users are stored in plain-text files (`/etc/passwd`, `/etc/shadow`, `/etc/group`). There's no GUI — everything is CLI. A user can belong to **many groups** simultaneously. `sudo` is your "Administrators" group — it's an explicit whitelist in `/etc/sudoers`, not a built-in group. Service accounts have `/usr/sbin/nologin` as their shell. Password policy uses `chage`. The most common mistake: adding a user to a group but forgetting to **log out and back in** for the change to take effect.
