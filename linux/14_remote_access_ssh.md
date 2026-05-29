# Module 14: Remote Access & SSH

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage remote access through:

```
Windows:
  Remote Desktop Protocol (RDP) → mstsc.exe → GUI remote access
  Get-NetTCPConnection → Check remote connections
  winrm quickconfig → Enable WinRM
  New-PSSession / Enter-PSSession → Remote PowerShell
  Invoke-Command -ComputerName → Remote command execution
  Start-Job -ScriptBlock → Background jobs
  psexec.exe → Remote execution (Sysinternals)
  Get-Service → Remote service status
  Copy-Item -ToSession → File transfer
  Test-NetConnection → Connectivity test
  netstat -ano → Active connections
  Get-NetTCPConnection → Remote sessions
  Get-PSSession → Active sessions
  Get-NetFirewallRule -Name *WinRM* → WinRM firewall rules
```

Windows remote access centers on **RDP** (GUI, port 3389), **WinRM** (remote PowerShell, port 5985/5986), and **PsExec** (command execution). Connections use domain credentials or local accounts.

## The Shift

Linux remote access centers on **SSH (port 22)** as the single unified protocol — terminal + file transfer + tunneling all in one. Unlike Windows (separate tools for GUI (RDP), remote management (WinRM), and execution (PsExec)), Linux uses **one tool (ssh)** for everything: remote shell, file transfer (scp/sftp), port forwarding, X11 forwarding, and bastion hosts. **SSH key auth** (not password) is the standard — like Windows smartcard/Certificate-based RDP but lighter. **No RDP on default server** — Linux servers rarely have GUIs; remote admin is **terminal-first**. **`su`/`sudo`** replaces `runas` for privilege escalation. **`tmux`/`screen`** replaces Windows session restore (RDP reconnect) for surviving network drops.

---

## SSH — Remote Shell Access

### SSH Client (Connecting to Remotes)

```bash
# SSH client (Windows: Enter-PSSession, Invoke-Command -ComputerName, ssh.exe)
ssh user@hostname              # Connect to remote server (Windows: Enter-PSSession -ComputerName)
ssh -p 2222 user@hostname      # Non-standard port (Windows: Enter-PSSession -Port 2222)
ssh user@192.168.1.100         # Connect by IP
ssh user@host -L 8080:localhost:80  # Local port forwarding (tunnel to remote)
ssh user@host -R 8080:localhost:80  # Remote port forwarding (reverse tunnel)
ssh user@host -D 1080          # Dynamic SOCKS proxy (Windows: Remote Desktop Gateway)
ssh -J user@bastion user@target  # Jump/bastion host (Windows: Invoke-Command -ComputerName via jump server)
ssh -Y user@host                # X11 forwarding (GUI apps over SSH)
ssh -N -f -L 3389:rdp-server:3389 user@gateway  # RDP over SSH tunnel
ssh -i ~/.ssh/id_ed25519 user@host  # Specific key
ssh -o StrictHostKeyChecking=no user@host  # Skip host key verification (first connect)
ssh -o ConnectTimeout=5 user@host  # Connection timeout
ssh -o ServerAliveInterval=60 user@host  # Keepalive (survive dropped connections)
ssh -T user@host "df -h"      # Remote command (Windows: Invoke-Command -ComputerName -ScriptBlock {df -h})
ssh user@host "command" > localfile  # Remote command output to local file
ssh user@host < localfile > remoteoutput  # Local file piped to remote stdin

# SSH aliases (Windows: Add-SSHPSSession or $PROFILE with Enter-PSSession defaults)
# ~/.ssh/config:
# Host web1
#   HostName 192.168.1.100
#   User admin
#   Port 2222
#   IdentityFile ~/.ssh/id_ed25519
#   ServerAliveInterval 60
# Host *
#   User admin
#   AddKeysToAgent yes
#   IdentitiesOnly yes
# Then: ssh web1
```

### SSH Server (Remote Access Setup)

```bash
# SSH server config (Windows: Configure-NetFirewallRule WinRM + Enable-PSRemoting)
sudo nano /etc/ssh/sshd_config
# Port 22                      → Change to non-standard port
# PermitRootLogin no           → Disable root login
# PasswordAuthentication no    → Key-only auth
# PubkeyAuthentication yes     → Enable key auth
# AuthorizedKeysFile .ssh/authorized_keys  → Key storage location
# ClientAliveInterval 300      → 5 min idle timeout
# ClientAliveCountMax 2        → Disconnect after 10 min idle
# MaxAuthTries 3               → Limit brute force attempts
# X11Forwarding no             → Disable X11 unless needed
# AllowTcpForwarding yes       → Enable port forwarding
# PermitEmptyPasswords no      → No empty passwords
# Protocol 2                   → SSHv2 only
# UseDNS no                    → Disable reverse DNS (faster auth)
# MaxSessions 10               → Max concurrent sessions
# AllowUsers admin deployer    → Limit users
# AllowGroups sshusers         → Limit groups
sudo systemctl restart sshd    # Apply changes

# SSH service management (Windows: Start-Service/Stop-Service/Restart-Service sshd)
sudo systemctl status sshd     # Check status
sudo systemctl enable sshd     # Auto-start on boot
sudo systemctl disable sshd    # Disable auto-start
sudo systemctl start sshd      # Start
sudo systemctl stop sshd       # Stop
```

---

## SSH Key Management

### Generate & Deploy Keys

```bash
# Key generation (Windows: ssh-keygen.exe for RDP cert auth)
ssh-keygen -t ed25519 -C "admin@server"  # Generate ED25519 key (recommended)
ssh-keygen -t rsa -b 4096 -C "admin@server"  # Generate RSA 4096-bit key
ssh-keygen -t ed25519 -N "" -C "deploy-bot"  # No passphrase (automation)
ssh-keygen -l -f ~/.ssh/id_ed25519.pub  # View key fingerprint
ssh-keygen -p -f ~/.ssh/id_ed25519     # Change passphrase
ssh-keygen -D pkcs11                  # View PKCS#11 token keys

# Deploy keys (Windows: Copy-Item -ToSession or New-PSSession for remote key copy)
ssh-copy-id user@remote              # Copy public key to remote server
ssh-copy-id -i ~/.ssh/id_ed25519 user@remote  # Specific key
ssh-copy-id user@remote 2>/dev/null  # Silent copy

# Manual key deploy (Windows: New-PSSession → New-Item $env:USERPROFILE\.ssh)
cat ~/.ssh/id_ed25519.pub | ssh user@remote "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
chmod 700 ~/.ssh                     # Directory permissions
chmod 600 ~/.ssh/authorized_keys     # Key file permissions

# Key management
ssh-agent bash                       # Start agent
ssh-add ~/.ssh/id_ed25519            # Add key to agent
ssh-add -l                           # List agent keys
ssh-add -D                           # Clear all keys
ssh-agent -s > /tmp/agent.sh && source /tmp/agent.sh  # Persist across sessions
```

---

## File Transfer

### SCP — Secure Copy

```bash
# SCP (Windows: Copy-Item -ToSession $session -Path "C:\file.txt" -Destination "\\remote\path")
scp file.txt user@remote:/home/user/  # Upload file
scp user@remote:/home/user/file.txt .  # Download file
scp -r /local/dir user@remote:/home/user/  # Upload directory
scp -r user@remote:/home/user/dir .  # Download directory
scp -P 2222 file.txt user@remote:/home/user/  # Non-standard port
scp -i ~/.ssh/id_ed25519 file.txt user@remote:/home/user/  # Specific key
scp -r -C dir1/ user@remote:/home/user/dir2/  # Compress during transfer
rsync -avz dir1/ user@remote:/home/user/dir2/  # Rsync (better for large transfers)
```

### SFTP — Secure FTP

```bash
# SFTP (Windows: Copy-Item -ToSession with SMB/CIFS share or New-PSDrive)
sftp user@remote                     # Interactive SFTP session
# Commands inside SFTP:
# put file.txt              # Upload
# get file.txt              # Download
# put -r dir/               # Upload directory
# get -r dir/               # Download directory
# ls                        # List remote files
# cd /remote/path           # Change remote directory
# lcd /local/path           # Change local directory
# ls -l                     # Long listing
# pwd                       # Remote working directory
# lpwd                      # Local working directory
# chmod 755 file.txt        # Change permissions on remote
# rm file.txt               # Remove remote file
# exit                      # Disconnect
```

---

## SSH Tunneling & Forwarding

### Local Port Forwarding

```bash
# Local forwarding (Windows: Test-NetConnection + Remote Desktop Gateway)
ssh -L 8080:localhost:80 user@server    # Access server:8080 → server:80 (Web server tunnel)
ssh -L 5432:localhost:5432 user@db-server  # PostgreSQL tunnel (Windows: Invoke-Command -ComputerName db-server)
ssh -L 3306:localhost:3306 user@db-server  # MySQL tunnel
ssh -L 9200:localhost:9200 user@server  # Elasticsearch tunnel
ssh -L 6379:localhost:6379 user@server  # Redis tunnel
ssh -L 27017:localhost:27017 user@server  # MongoDB tunnel
ssh -L 8443:internal-app:8443 user@gateway  # Forward through jump host
```

### Remote Port Forwarding

```bash
# Remote forwarding (Windows: WinRM reverse shell or PowerShell remoting)
ssh -R 8080:localhost:3000 user@server  # Expose local:3000 as server:8080 (dev web server exposed)
ssh -R 0.0.0.0:8080:localhost:3000 user@server  # Bind to all interfaces
ssh -R 9200:localhost:9200 user@server  # Elasticsearch exposed on server
```

### Dynamic Port Forwarding (SOCKS Proxy)

```bash
# Dynamic forwarding (Windows: Proxy settings in IE/Edge or netsh winhttp)
ssh -D 1080 user@server                  # SOCKS proxy on localhost:1080
ssh -D 1080 -N -f user@server            # Background SOCKS proxy
# Browser: Configure SOCKS proxy → localhost:1080 (Windows: Internet Options → LAN Settings)
```

### SSH Gateway / Bastion Host

```bash
# Bastion host (Windows: Invoke-Command -ComputerName jumpbox → Invoke-Command -ComputerName target)
# ~/.ssh/config:
# Host bastion
#   HostName jump.company.com
#   User admin
#
# Host web-*
#   ProxyJump bastion
#   User deployer
#
# Then: ssh web-prod1
# Or: ssh web-prod1 "systemctl status nginx"

# Alternative: ProxyCommand
ssh -o ProxyJump=user@bastion user@target
ssh -o ProxyCommand="ssh -W %h:%p user@bastion" user@target  # Older syntax
```

---

## Remote Command Execution

### SSH One-Liners (No Interactive Session)

```bash
# Remote command (Windows: Invoke-Command -ComputerName server -ScriptBlock { command })
ssh user@server "uptime"                  # Simple command
ssh user@server "df -h && free -m"        # Multiple commands
ssh user@server "sudo systemctl status nginx"  # With sudo
ssh user@server "cat /etc/passwd"         # View remote file
ssh user@server "sudo tail -f /var/log/syslog"  # Remote log follow
ssh user@server "mkdir -p /tmp/test"      # Create remote directory
ssh user@server "rm -rf /tmp/test"        # Remove remote directory
ssh user@server "wget http://example.com/file.tar.gz -O /tmp/"  # Download remote
ssh user@server "bash -s" < local-script.sh  # Run local script remotely
ssh user@server "tar czf - /data/" | tar xzf - -C /backup/  # Remote to local archive
ssh user@server "cat /data/bigfile.dat" > /local/bigfile.dat  # Stream file
```

### Parallel Execution

```bash
# Parallel SSH (Windows: Invoke-Command -ComputerName @servers -ScriptBlock)
# For multiple servers:
for server in server1 server2 server3; do
    ssh $server "uptime" &
done
wait  # Wait for all to finish

# Using pdsh (parallel distribution shell)
apt install pdsh
pdsh -w user@{server1,server2,server3} "uptime"
```

### Tmux / Screen — Survive Dropped Connections

```bash
# Tmux (Windows: PSEventViewer or PowerShell background jobs for persistence)
tmux new -s mysession    # Create new session
tmux ls                  # List sessions
tmux attach -t mysession  # Reattach to session
tmux kill-session -t mysession  # Kill session
# Inside tmux:
# Ctrl+b, d → Detach (survives network drop)
# Ctrl+b, n → New window
# Ctrl+b, " → Split pane horizontally
# Ctrl+b, % → Split pane vertically
# Ctrl+b, & → Kill pane

# Screen (alternative to tmux)
apt install screen
screen -S mysession      # Create session
screen -r mysession      # Reattach
screen -ls               # List sessions
# Ctrl+a, d → Detach
```

---

## Other Remote Access Methods

### sudo — Privilege Escalation

```bash
# sudo (Windows: runas /user:admin command or Start-Process -Verb RunAs)
sudo apt update          # Run as root (Windows: admin prompt UAC)
sudo nano /etc/hosts     # Edit as root
sudo whoami              # Verify root (Windows: whoami /priv)
sudo -u www-data whoami  # Run as specific user (Windows: runas /user:www-iis command)
sudo -l                  # List allowed commands (Windows: Get-NetGroupMember Domain\Group | Format-List)
sudo -b apt update       # Background sudo
sudo -i                  # Interactive root shell (Windows: Start-Process powershell -Verb RunAs)
sudo !!                  # Repeat last command as root (Windows: & ($History.HistoryList[-1]) with admin)

# /etc/sudoers (Windows: Group Policy → Restricted Groups)
sudo visudo              # Edit sudoers safely
# user ALL=(ALL) ALL     # Full root access
# user ALL=(www-data) NOPASSWD: /usr/bin/nginx  # Specific user, specific command
# %admin ALL=(ALL) ALL   # Admin group full access
# Defaults timestamp_timeout=5  # sudo timeout 5 min (Windows: Credential Manager caching)
# Defaults !rootpw       # Don't require root password
# Defaults !authenticate # Allow sudo without password (use carefully)
```

### SCP vs Rsync (File Transfer)

```bash
# SCP vs Rsync (Windows: Copy-Item -ToSession vs robocopy /mir)
scp file.txt user@host:/dest/    # SCP copy
rsync -avz file.txt user@host:/dest/  # Rsync (incremental, faster for large files)
rsync -avz --progress dir/ user@host:/dest/  # With progress bar
rsync -avz -e "ssh -p 2222" dir/ user@host:/dest/  # With SSH options
rsync -avz --delete dir/ user@host:/dest/  # Mirror (delete extras on remote)
rsync -avz --dry-run dir/ user@host:/dest/  # Preview changes
rsync -avz -e "ssh -i ~/.ssh/id_ed25519" dir/ user@host:/dest/  # With key file
```

---

## Remote Connectivity & Diagnostics

### Network Connectivity

```bash
# Connectivity (Windows: Test-NetConnection, Test-WSMan)
ping server                      # Ping (Windows: Test-Connection)
nc -zv server 22                 # Check port open (Windows: Test-NetConnection -Port 22)
nc -zv server 80                 # Check port
telnet server 22                 # Test connection (install: sudo apt install telnet)
curl -I https://server           # HTTP headers (Windows: Invoke-WebRequest)
curl -I http://server:8080       # Check web service
ssh -v user@server               # Verbose SSH connection (debug)
ssh -vvv user@server             # Very verbose
netcat -l -p 8080               # Listen on port (Windows: netstat or PowerShell TCP listener)
```

### Remote Session Management

```bash
# Session management (Windows: Get-PSSession, Get-NetTCPConnection)
who                              # Who's logged in
w                              # Detailed login info
last                           # Login history
lastlog                        # All login history
whoami                         # Current user
whoami -all                    # Full user info (Windows: whoami /all)
id                             # User/group IDs
ps aux | grep ssh                # SSH processes
ss -tunapl | grep :22            # SSH listeners (Windows: Get-NetTCPConnection -State Listen)
netstat -tunapl | grep :22       # SSH listeners (Windows: netstat -ano)
```

---

## Hands-On Exercise

```bash
# 1. SSH basics
ssh-keygen -t ed25519 -C "admin@server"
ssh-copy-id user@remote
ssh user@remote
uptime
df -h
free -m
exit

# 2. SSH config (persistent shortcuts)
~/.ssh/config:
# Host myserver
#   HostName 192.168.1.100
#   User admin
#   Port 22
#   IdentityFile ~/.ssh/id_ed25519
#   ServerAliveInterval 60
ssh myserver

# 3. Remote commands (no interactive session)
ssh myserver "df -h && free -m"
scp file.txt myserver:/home/admin/
rsync -avz --progress dir/ myserver:/home/admin/

# 4. Port forwarding
ssh -L 8080:localhost:80 myserver  # Web tunnel
ssh -L 5432:localhost:5432 dbserver  # Database tunnel

# 5. Tmux
tmux new -s demo
uptime
tmux detach  # (Ctrl+b, d)
tmux attach -t demo  # Reattach

# 6. SSH hardening
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
# PasswordAuthentication no
# Port 2222 (optional)
# AllowUsers admin deployer
sudo systemctl restart sshd
```

---

## Mental Model Shift

| Windows Remote Access Mindset | Linux Remote Access Mindset |
|--|--|
| RDP (mstsc.exe, port 3389) for GUI remote access | SSH (port 22) for terminal remote access (no default GUI) |
| Enter-PSSession / Invoke-Command for remote PowerShell | ssh user@host for remote shell |
| New-PSSession / Enter-PSSession | ssh user@host (or ssh config Host alias) |
| Test-NetConnection -Port 22 | nc -zv server 22 or ssh -v user@server |
| Copy-Item -ToSession $session | scp or rsync -avz |
| Copy-Item -ToSession $session -Path "C:\file" -Destination "\\remote\path" | scp file.txt user@host:/path/ |
| Start-Job for background jobs | tmux / screen for session persistence |
| PsExec for remote execution | ssh user@host "command" |
| PsExec -s command (system account) | ssh user@host "sudo command" |
| runas /user:admin command | sudo command or sudo -i |
| runas /user:www-iis command | sudo -u www-iis command |
| netstat -ano | ss -tunapl |grep :22 or netstat -tunapl |
| Get-NetTCPConnection | ss -tunapl or netstat -tunapl |
| Test-WSMan | ssh -v user@server or nc -zv server 22 |
| Get-PSSession | tmux ls or who / w |
| Exit-PSSession | exit |
| Disable-PSRemoting / Enable-PSRemoting | systemctl stop sshd / systemctl start sshd |
| WinRM (port 5985/5986) for remote management | SSH (port 22) for everything |
| Invoke-Command -ComputerName @servers -ScriptBlock | pdsh -w user@{s1,s2,s3} or for loop with ssh |
| Invoke-Command via proxy / jump box | ssh -J user@bastion user@target |
| Invoke-Command -Port 5986 (WinRM HTTPS) | ssh -p 2222 user@host (non-standard port) |
| New-SmbShare for remote file access | scp / rsync / sftp |
| New-PSDrive -Name Z -Root "\\\\server\\\\share" | mount -t cifs //server/share /mnt/smb |
| Windows Defender blocking remote (smart screen) | ssh -o StrictHostKeyChecking=no (first connect) |
| RDP Gateway (NLA, cert validation) | SSH key-based auth (ssh-copy-id) |
| RDP session restore on reconnect | tmux attach -t session (survives drops) |
| RDP clipboard redirect | xclip or scp (clipboard via files) |
| RDP audio/video redirect | No direct equivalent (terminal-first) |
| RemoteApp / RD Web Access | VNC / X2Go / noVNC for GUI |
| Get-NetFirewallRule -Name *WinRM* | ufw status / nft list ruleset |
| Configure-NetFirewallRule for WinRM | ufw allow ssh / sshd_config |
| Test-NetConnection server -Port 3389 | nc -zv server 22 |
| Enable-WSManTracing | ssh -vvv user@server |
| $PSSessionConfigurationName | IdentityFile ~/.ssh/id_ed25519 |
| New-ScheduledTask (run remote) | crontab -e on remote host |
| Windows Credential Manager for remote auth | SSH agent (ssh-agent + ssh-add) |
| Windows Trusted Hosts list (~/.ssh/config ProxyJump) | ProxyJump or ProxyCommand in ssh config |
| Group Policy → Remote Desktop Services | PAM (/etc/pam.d/sshd) → SSH access control |
| Active Directory → domain-joined RDP | DNS + ssh config → host-agnostic SSH |
| RDP → full desktop control | SSH → terminal control (GUI via VNC/X2Go if needed) |
| Remote Desktop → port 3389 (fixed) | SSH → configurable port (default 22, often changed) |
| Remote Desktop → RDP file (.rdp) for connection config | ~/.ssh/config → Host alias for connection config |
| Remote Desktop → disconnect/resume session | tmux attach -t session → resume session |
| Get-SmbSession → remote sessions | who / w → logged-in users |
| Get-NetTCPConnection -State Established | ss -tunapl |grep ESTAB → active connections |
| Enable-PSRemoting -Force | systemctl enable --now sshd |
| Disable-PSRemoting | systemctl disable sshd |
| Set-Item wsman:\localhost\WinRM\Config\MaxTimeouts | /etc/ssh/sshd_config ClientAliveInterval |
| Get-ChildItem Cert: LocalMachine\My | /etc/ssl/certs/ or /etc/ssh/ssh_host_*_key.pub |
| Get-ChildItem Cert: CurrentUser\My | ~/.ssh/id_ed25519.pub (user SSH keys) |
| winrm enumerate winrm/config/listener | ss -tunapl | grep :22 (SSH listener) |

**Key takeaway:** Linux remote administration is **terminal-first and protocol-agnostic** — SSH (port 22) replaces RDP (GUI), WinRM (PowerShell remoting), and PsExec (command execution) in one tool. **SSH key auth** (not password) is the standard — `ssh-keygen` → `ssh-copy-id` → `ssh user@host`. **`~/.ssh/config`** replaces `.rdp` files — define Host aliases, ports, keys, and jump hosts in one place. **`tmux`/`screen`** survives dropped connections (Windows: RDP reconnect). **`scp`/`sftp`/`rsync`** replace Copy-Item -ToSession for file transfers. **Port forwarding** (`-L`/`-R`/`-D`) turns SSH into a tunnel for databases, web servers, or SOCKS proxy. **`sudo`** replaces `runas` for privilege escalation. **No RDP on default servers** — Linux servers are CLI-first; GUI remote access needs separate installation (VNC/X2Go/noVNC). **Network shares**: SMB uses `mount -t cifs`, NFS uses `mount -t nfs`, not a built-in "share" command like New-SmbShare.
