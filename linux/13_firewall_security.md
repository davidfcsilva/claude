# Module 13: Firewall & Security

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage firewall and security through:

```
Windows:
  Windows Defender Firewall with Advanced Security (wf.msc) → GUI
  Get-NetFirewallRule → List all rules
  Get-NetFirewallProfile → Firewall profiles (Domain, Private, Public)
  New-NetFirewallRule → Create inbound/outbound rule
  Remove-NetFirewallRule → Delete rule
  Disable-NetFirewallRule / Enable-NetFirewallRule → Toggle rules
  Set-NetFirewallRule → Modify rule
  Get-NetIPSecurityPolicy → IP security policies
  Get-NetAdapterFirewall → Interface-level firewall
  netsh advfirewall show allprofiles → Show firewall status
  netsh advfirewall set allprofiles state on → Enable firewall
  netsh advfirewall firewall add rule → Add rule via CLI
  Get-NetConnectionProfile → Network profiles (Public/Private/Domain)
  netsh advfirewall export C:\fw.wfw → Export firewall config
  Export-CimInstance -ClassName MSFT_NetFirewallRule → Export rules
```

Windows firewall uses **profiles** (Domain, Private, Public) with **rules** (inbound/outbound) and **IP security policies**. Rules are applied per-profile with `New-NetFirewallRule` and managed via `wf.msc`.

## The Shift

Linux firewalls are **rule-based and stateful** — `ufw` (simple) and `nftables/iptables` (advanced). Linux has **no Windows-style profile concept** — instead, you bind rules to **network interfaces** (eth0, wlan0) or **zones** (firewalld). Linux security is also **distributed** — no Group Policy equivalent in a single tool. **Key differences**: Linux firewall syntax is more complex but more flexible; `ufw` abstracts this for simplicity. Linux uses **SSH (port 22)** as the primary remote access method, so firewall rules must allow SSH before disabling password auth. **Linux has no "Domain Profile"** — it trusts your network config (interface name or zone). **Linux security** relies on **SSH key auth** (not Windows Credential Manager), **fail2ban** (not Windows SmartScreen), and **AppArmor/SELinux** (not Windows AppContainer).

---

## UFW — Uncomplicated Firewall

### Status & Profiles

```bash
# Status (Windows: Get-NetFirewallProfile)
ufw status                      # Simple status
ufw status verbose              # Detailed (ports, rules)
ufw status numbered             # Rule numbers
ufw default allow outgoing      # Default policies (Windows: Set-NetFirewallProfile -DefaultOutputAction Allow)
ufw default deny incoming       # Default policies (Windows: Set-NetFirewallProfile -DefaultInputAction Block)
ufw show rawdefault             # Raw default rules

# Enable/disable (Windows: Enable-NetFirewallProfile -All)
ufw enable                      # Enable firewall
ufw disable                     # Disable firewall (Windows: Disable-NetFirewallProfile -All)
ufw reset                       # Reset to defaults (Windows: netsh advfirewall reset)
ufw logging on|off|low|medium|high|full  # Logging level
```

### Default Policies

```bash
# Default policies (Windows: Set-NetFirewallProfile -DefaultInboundAction Block -DefaultOutputAction Allow)
ufw default deny incoming       # Block all inbound by default
ufw default allow outgoing      # Allow all outbound by default
ufw default deny incoming        # Block all inbound by default
ufw default allow outgoing       # Allow all outbound by default
```

### Allow Rules

```bash
# Allow rules (Windows: New-NetFirewallRule -Direction Inbound -Action Allow)
ufw allow 22/tcp                # Allow SSH (Windows: New-NetFirewallRule -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow)
ufw allow ssh                   # Allow SSH (alias for port 22/tcp)
ufw allow 80/tcp                # Allow HTTP
ufw allow 443/tcp               # Allow HTTPS
ufw allow 8080/tcp              # Allow custom port
ufw allow proto tcp from 192.168.1.0/24 to any port 22  # From specific subnet
ufw allow from 10.0.0.0/8       # From entire subnet
ufw allow in on eth0 to any port 80   # Interface-specific rule
ufw allow 80/tcp                # Allow TCP port 80
ufw allow 80                    # Allow TCP or UDP port 80
ufw allow 80/udp                # Allow UDP port 80
ufw allow 53/tcp,53/udp         # Allow DNS on both TCP and UDP
ufw allow 1024:1068/tcp         # Port range
ufw allow from 192.168.1.100    # Allow all ports from specific IP
```

### Deny & Reject

```bash
# Block rules (Windows: New-NetFirewallRule -Direction Inbound -Action Block)
ufw deny 23/tcp                 # Deny telnet
ufw deny from 10.0.0.5          # Block specific IP
ufw deny 80/tcp                 # Deny port 80
ufw reject 80/tcp               # Reject with ICMP admin prohibited
ufw deny in on eth0             # Block all on interface
ufw deny out on eth1 to any     # Block outbound on interface
```

### Delete Rules

```bash
# Delete rules (Windows: Remove-NetFirewallRule -Name "MyRule")
ufw delete allow 22/tcp         # Delete by action/port
ufw delete allow ssh            # Delete SSH rule
ufw delete 8                    # Delete rule #8 (by number)
ufw delete numbered             # Delete by number
ufw delete status               # Delete all rules
ufw delete allow 80/tcp         # Delete specific rule
ufw delete allow from 10.0.0.5  # Delete IP-based rule
```

---

## nftables / iptables — Advanced Firewall

### nftables (Modern Replacement)

```bash
# nftables (Windows: netsh advfirewall firewall add rule / New-NetFirewallRule)
# nftables is the modern firewall — replaces iptables, ip6tables, arptables, ebtables
apt install nftables            # Install nftables
systemctl enable --now nftables # Enable nftables service
nft list ruleset                # List all rules (Windows: Get-NetFirewallRule | Format-Table)
nft add table inet filter       # Create a table
nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'  # Default drop
nft add chain inet filter forward '{ type filter hook forward priority 0; policy drop; }'
nft add chain inet filter output '{ type filter hook output priority 0; policy accept; }'

# Add rules
nft add rule inet filter input tcp dport 22 accept          # Allow SSH
nft add rule inet filter input tcp dport { 80, 443 } accept # Allow HTTP/HTTPS
nft add rule inet filter input ct state established,related accept  # Allow established connections
nft add rule inet filter input iif lo accept                 # Allow loopback
nft add rule inet filter input icmp type echo-request accept # Allow ping

# Save/restore rules
nft list ruleset > /etc/nftables.conf   # Save rules (Windows: Export-CimInstance -ClassName MSFT_NetFirewallRule)
nft -f /etc/nftables.conf               # Load rules from file
systemctl restart nftables              # Apply changes
```

### iptables (Legacy but Still Common)

```bash
# iptables (Windows: netsh advfirewall firewall add rule name="SSH" dir=in action=allow protocol=TCP localport=22)
iptables -L                         # List rules (Windows: Get-NetFirewallRule | Format-Table)
iptables -L -n -v                  # Detailed (with packet counts)
iptables -L -n -v --line-numbers   # With rule numbers
iptables -F                         # Flush all rules
iptables -A INPUT -p tcp --dport 22 -j ACCEPT  # Allow SSH (Windows: New-NetFirewallRule -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow)
iptables -A INPUT -p tcp --dport 80 -j ACCEPT  # Allow HTTP
iptables -A INPUT -p tcp --dport 443 -j ACCEPT # Allow HTTPS
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT  # Allow established connections
iptables -A INPUT -i lo -j ACCEPT                # Allow loopback
iptables -A INPUT -j DROP                       # Default drop
iptables -I INPUT 1 -p tcp --dport 8080 -j ACCEPT  # Insert at position 1
iptables -D INPUT 1                         # Delete rule at position 1
iptables -A INPUT -s 10.0.0.5 -j DROP       # Block specific IP
iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT  # Allow subnet
iptables-save > /etc/iptables/rules.v4       # Save rules
iptables-restore < /etc/iptables/rules.v4    # Restore rules
```

---

## Network Security

### SSH Security

```bash
# SSH hardening (Windows: Restrict-NetFirewallRule or disable RDP, use VPN)
sudo nano /etc/ssh/sshd_config
# Port 22                              → Change to non-standard port (Windows: change RDP port)
# PermitRootLogin no                   → Disable root login (Windows: disable built-in Administrator)
# PasswordAuthentication no            → Key-only auth (Windows: Windows Hello for Business or Smart Card)
# PermitEmptyPasswords no              → No empty passwords
# MaxAuthTries 3                       → Limit attempts (Windows: account lockout policy)
# AllowUsers admin deployer            → Allow specific users (Windows: Deny ACL on RDP)
# ClientAliveInterval 300              → Keepalive
# ClientAliveCountMax 2                → Disconnect after 10 min idle
# X11Forwarding no                     → Disable X11
# UseDNS no                            → Disable DNS lookup
systemctl restart sshd                 # Apply changes

# SSH key setup (Windows: ssh-keygen equivalent is keygen.exe for RDP cert-based auth)
ssh-keygen -t ed25519 -C "admin@server"  # Generate key
ssh-copy-id user@remote                  # Copy public key
ssh user@remote -i ~/.ssh/id_ed25519     # Connect with key
```

### Fail2Ban — Brute Force Protection

```bash
# Fail2Ban (Windows: Windows Defender SmartScreen / account lockout policy)
apt install fail2ban                  # Install fail2ban
systemctl enable --now fail2ban       # Enable
cat /etc/fail2ban/jail.local          # Config
# [sshd]
# enabled = true
# port = ssh
# filter = sshd
# logpath = /var/log/auth.log
# maxretry = 3
# bantime = 3600
# findtime = 600
# banaction = iptables-multiport

# Check status
fail2ban-client status                # All jails
fail2ban-client status sshd           # SSH jail
fail2ban-client set sshd banip 10.0.0.5  # Ban IP manually
fail2ban-client set sshd unbanip 10.0.0.5  # Unban IP

# Common jails (Windows: Windows Defender SmartScreen for email, SmartScreen for browsers)
# [sshd] → SSH brute force (Windows: account lockout policy)
# [apache-auth] → Web auth (Windows: IIS URL Authorization)
# [postfix] → Mail (Windows: Exchange Edge Transport rule)
# [dovecot] → Mail (Windows: Exchange Edge Transport rule)
# [nginx-http-auth] → Web auth (Windows: IIS URL Authorization)
# [recidive] → Repeat offenders (Windows: escalating lockout)
```

---

## AppArmor & SELinux — Mandatory Access Control

### AppArmor (Ubuntu Default)

```bash
# AppArmor (Windows: Windows Defender Application Control / AppLocker)
dpkg -l | grep apparmor              # Check installed
aa-status                              # AppArmor status
aa-status --json                       # JSON output
aa-enforce /etc/apache2/apache2.conf # Enforce profile
aa-disable /etc/apache2/apache2.conf # Disable profile
aa-logprof                             # Auto-generate profiles from logs
cat /etc/apparmor.d/apache2            # Apache profile
```

### SELinux (RHEL/CentOS Default)

```bash
# SELinux (Windows: Windows Defender Application Control)
sestatus                             # Status
getenforce                           # Enforcing/Permissive/Disabled
setenforce 0                         # Permissive mode
setenforce 1                         # Enforcing mode
semanage fcontext -a -t httpd_sys_content_t "/var/www(/.*)?"  # Set file context
restorecon -Rv /var/www            # Apply context
ausearch -m avc -ts recent         # Audit SELinux denials
semanage port -a -t http_port_t -p tcp 8080  # Allow port in SELinux
```

---

## Encryption & Certificates

### File Encryption

```bash
# File encryption (Windows: BitLocker, Encrypt-File)
gpg -c file.txt                    # Encrypt with GPG
gpg file.txt.gpg                   # Decrypt GPG file
openssl enc -aes-256-cbc -salt -in file.txt -out file.enc -pass pass:mypassword  # Encrypt with OpenSSL
openssl enc -aes-256-cbc -d -in file.enc -out file.txt -pass pass:mypassword  # Decrypt
dmsetup-mkfile /etc/dm-crypt/keyfile  # Disk encryption key
cryptsetup luksFormat /dev/sdb1    # LUKS disk encryption (Windows: BitLocker/New-BitLockerVolume)
cryptsetup luksOpen /dev/sdb1 secure   # Open LUKS volume
cryptsetup luksClose secure            # Close LUKS volume
```

### TLS/SSL Certificates

```bash
# Certificate management (Windows: certlm.msc, Get-ChildItem Cert:)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt  # Self-signed
openssl x509 -in server.crt -text    # View certificate
openssl s_client -connect example.com:443  # Test remote cert
openssl x509 -checkend 86400 -noout  # Check if cert expires in 24h
openssl verify -CAfile ca.crt server.crt  # Verify cert chain
certbot certonly --standalone -d example.com  # Free Let's Encrypt cert
```

### Disk Encryption

```bash
# Disk encryption (Windows: BitLocker, Manage-Bde)
apt install cryptsetup               # Install cryptsetup
cryptsetup luksFormat /dev/sdb1      # Encrypt disk (Windows: New-BitLockerVolume)
cryptsetup luksOpen /dev/sdb1 encrypted  # Open encrypted volume
mkfs.ext4 /dev/mapper/encrypted      # Format
mount /dev/mapper/encrypted /mnt/secure  # Mount
cryptsetup luksClose encrypted       # Close/lock
```

---

## System Security Basics

### Password Policy

```bash
# Password policies (Windows: net accounts / Group Policy: Account Policies)
# /etc/login.defs — password aging
PASS_MAX_DAYS 90          # Max days before password change
PASS_MIN_DAYS 1           # Min days before change allowed
PASS_WARN_AGE 7           # Days to warn before expiration
# /etc/pam.d/common-password — complexity
# password requisite pam_pwquality.so retry=3 minlen=12 dcredit=-1 ucredit=-1 ocredit=-1 lcredit=-1
# /etc/security/access.conf — login restrictions
root : ALL EXCEPT 192.168.1.0/24 : EXCEPT ALL  # Allow root only from subnet
user : ALL : ALL          # All users login from anywhere
```

### SSH Hardening Checklist

```bash
# SSH security checklist (Windows: RDP security + GPO restrictions)
# 1. Change SSH port (non-standard)
# 2. Disable root login (PermitRootLogin no)
# 3. Key-only authentication (PasswordAuthentication no)
# 4. Limit users (AllowUsers admin deployer)
# 5. Set idle timeout (ClientAliveInterval 300)
# 6. Disable X11 forwarding (X11Forwarding no)
# 7. Enable fail2ban (protect against brute force)
# 8. Use SSH certificate auth for large deployments
# 9. Restrict to specific networks if possible
# 10. Regular key rotation
```

---

## Hands-On Exercise

```bash
# 1. Firewall basics
ufw status                 # Current status
ufw default deny incoming  # Default deny
ufw default allow outgoing # Default allow
ufw enable                 # Enable firewall (test with SSH first!)

# 2. Add rules
ufw allow ssh              # SSH
ufw allow 80/tcp           # HTTP
ufw allow 443/tcp          # HTTPS
ufw allow from 192.168.1.0/24 to any port 22  # Subnet SSH
ufw status numbered        # Verify rules

# 3. SSH hardening
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
# PasswordAuthentication no
sudo systemctl restart sshd

# 4. Install fail2ban
sudo apt install fail2ban
sudo systemctl status fail2ban
fail2ban-client status sshd

# 5. nftables
sudo apt install nftables
sudo nft list ruleset
sudo systemctl enable --now nftables
```

---

## Mental Model Shift

| Windows Security Mindset | Linux Security Mindset |
|--|--|
| Windows Defender Firewall GUI (wf.msc) | `ufw status` / `nft list ruleset` / `iptables -L` (CLI) |
| Get-NetFirewallRule | `ufw status` or `nft list ruleset` |
| New-NetFirewallRule | `ufw allow 22/tcp` |
| Remove-NetFirewallRule | `ufw delete allow 22` |
| Set-NetFirewallProfile -DefaultInputAction Block | `ufw default deny incoming` |
| netsh advfirewall show allprofiles | `ufw status` or `ufw show rawdefault` |
| Firewall profiles (Domain/Private/Public) | Interface-based rules (`ufw allow in on eth0`) or nftables zones |
| Windows Defender SmartScreen (email/browsers) | `fail2ban` (brute force protection) |
| SmartScreen / account lockout | `fail2ban` (SSH, Apache, Postfix jails) |
| Windows Defender Application Control / AppLocker | AppArmor / SELinux |
| BitLocker (drive encryption) | `cryptsetup luksFormat` |
| Manage-Bde | `cryptsetup` |
| Get-ChildItem Cert: | `openssl x509 -text` |
| certlm.msc (certificates) | `openssl req` / `certbot` |
| Get-SmbShare | `lsmod | grep nfs` or `showmount -e` |
| New-SmbShare / Remove-SmbShare | `exportfs` (NFS) or `smbd` (Samba) |
| netsh advfirewall firewall add rule | `ufw allow` / `iptables -A` |
| netsh advfirewall firewall delete rule | `ufw delete allow` / `iptables -D` |
| Enable-NetFirewallProfile -All | `ufw enable` |
| Disable-NetFirewallProfile -All | `ufw disable` |
| Export-CimInstance firewall rules | `ufw status numbered` / `iptables-save` |
| Firewall event log (Microsoft-Windows-Firewall/State) | `/var/log/syslog` / `dmesg` / `ufw logging` |
| RDP (port 3389) default for remote admin | SSH (port 22) default for remote admin |
| RDP / port 3389 → non-standard port | SSH → port change + key auth |
| RDP session management | `who`, `w`, `last`, `whoami` |
| Windows Remote Management (WinRM/5985) | SSH + `sudo` |
| PsExec (remote execution) | SSH + `sudo` + `scp` / `rsync` |
| Windows Firewall + SmartScreen + AppLocker + BitLocker (all in Defender) | Linux: separate tools (ufw, fail2ban, AppArmor, cryptsetup) |
| Group Policy (centralized security) | PAM (Pluggable Authentication Modules) — `/etc/pam.d/` |
| Windows account lockout policy | `fail2ban` + `pam_tally2` or `faillock` |
| Windows Defender scanning logs | `journalctl -k \| grep -i "apparmor\|selinux"` |

**Key takeaway:** Linux firewall management is **CLI-driven** — use `ufw` for simple setups (`ufw allow 22/tcp`, `ufw default deny incoming`) and `nftables`/`iptables` for advanced needs. Unlike Windows Defender Firewall (all-in-one GUI with profiles), Linux separates concerns: **ufw** for firewall, **fail2ban** for brute force protection, **AppArmor/SELinux** for mandatory access control, and **cryptsetup** for disk encryption. **Always enable the firewall before locking down SSH** — the #1 mistake is `ufw enable` + `PasswordAuthentication no` = locked out server. **SSH key auth** (not password) is the Linux standard for remote administration (Windows: RDP with SmartCard/Windows Hello). **Fail2ban** (brute force protection) is the closest to Windows SmartScreen/account lockout — it blocks IPs after repeated failures. **No single tool** manages all security (Windows Defender does everything); Linux uses **modular tools** — each tool does one thing well. **Network shares**: NFS uses `exportfs`/`mount -t nfs`, SMB uses `smbd`/`mount -t cifs`. **Disk encryption**: `cryptsetup luksFormat` (like BitLocker). **Certificate management**: `openssl` (like certlm.msc). **`/etc/login.defs`** manages password aging (like Windows account policy GPO). **`/etc/pam.d/`** manages authentication (like Windows account policies).
