# Module 9: Networking

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage networking through:

```
Windows:
  ipconfig /all → IP addresses and DNS
  Get-NetIPConfiguration, Get-NetIPAddress → PowerShell
  Get-NetAdapter → Network interfaces
  Get-NetTCPConnection → Active connections
  Test-NetConnection → Ping/traceroute
  Set-NetIPAddress → Configure IP
  ipconfig /release, ipconfig /renew → DHCP
  route print → Routing table
  nslookup, Resolve-DnsName → DNS
  netsh advfirewall → Firewall
  Get-NetFirewallRule → Firewall rules
  nmap → Port scanning
```

Windows networking is **Get-Net* cmdlet-driven** with `ipconfig` as the legacy CLI. Interfaces are managed via **Network Connections** (GUI) or `Set-NetIPAddress` (PowerShell). DNS, routing, and firewall are separate command families.

## The Shift

Linux networking is **file and socket-driven**. There are no PowerShell cmdlets — everything is `ifconfig` (deprecated), `ip` (modern), `/etc/netplan/` or `/etc/network/interfaces` (config), and `ss`/`lsof` (connections). Network configuration lives in **files**, not in the registry. Unlike Windows where `Get-Net*` covers everything, Linux splits networking into multiple tools: `ip`, `ss`, `dig`, `nslookup`, `iptables`, `firewalld`, `nftables`, `netplan`.

---

## Interface Configuration

### View Network Interfaces

```bash
# List interfaces (Windows: Get-NetAdapter, ipconfig /all)
ip addr show                          # Show all interfaces (modern, replaces ifconfig)
ip link show                          # Layer 2 link info
ip -s link                          # Statistics (packets in/out)

# Traditional (deprecated but still widely used)
ifconfig -a                           # All interfaces (legacy)
iwconfig                              # Wireless interfaces

# Filtered view (Windows: Get-NetAdapter | Where-Object Status -eq 'Up')
ip -br addr                         # Brief/compact view (fastest)
ip addr show | grep inet             # Only IPv4 addresses
ip addr show | grep inet6            # Only IPv6 addresses
cat /proc/net/dev                     # Kernel's interface view
```

### Configure IP Addresses

```bash
# Configure interfaces (Windows: Set-NetIPAddress, Set-NetAdapterAdvancedProperty)
# Note: Changes are temporary until saved to config file!

# Set IP (temporary — lost on reboot)
sudo ip addr add 192.168.1.50/24 dev eth0   # Add IP to interface
sudo ip link set eth0 up                      # Bring interface up
sudo ip link set eth0 down                    # Bring interface down

# Configure DNS (Windows: Set-DnsClientServerAddress)
# DNS config is in /etc/resolv.conf (like Windows %windir%\System32\drivers\etc\hosts)
cat /etc/resolv.conf                         # DNS servers
nameserver 8.8.8.8
nameserver 8.8.4.4
search example.com

# Persistent config (Ubuntu Netplan) — Windows: Set-NetIPAddress -Persistent
cat /etc/netplan/01-netcfg.yaml
```

YAML for Netplan (Ubuntu 20.04+ default):

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true                    # DHCP (like Windows: obtain IP automatically)
      # OR static config:
      addresses:
        - 192.168.1.50/24
      gateway4: 192.168.1.1          # Default gateway
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4] # DNS servers
```

Apply netplan config (Windows: Set-DnsClientServerAddress):

```bash
sudo netplan apply                    # Apply netplan config
sudo netplan try                      # Apply with 120s rollback on failure
```

### DHCP

```bash
# DHCP (Windows: ipconfig /release + ipconfig /renew)
sudo dhclient eth0                    # Request DHCP lease
sudo dhclient -r eth0                 # Release DHCP lease
systemctl status systemd-networkd     # Network service status
```

---

## Connectivity and Diagnostics

### Check Connectivity

```bash
# Ping (Windows: ping, Test-NetConnection)
ping google.com                       # Ping by hostname
ping -c 4 google.com                  # 4 pings (Windows: default is continuous)
ping -c 1 -W 2 google.com             # 1 ping, 2s timeout
ping -I eth0 google.com               # Ping from specific interface

# Test connection (Windows: Test-NetConnection google.com -Port 443)
nc -zv google.com 443                  # Test TCP port connectivity
nc -zv -w 2 192.168.1.1 22            # Test port with timeout
timeout 2 bash -c 'cat < /dev/null > /dev/tcp/google.com/443'  # TCP check without nc
```

### Traceroute

```bash
# Traceroute (Windows: tracert)
traceroute google.com                   # Linux traceroute
tracepath google.com                    # Alternative traceroute (no root needed)
mtr google.com                          # My traceroute — combines ping + traceroute
mtr -r google.com                       # Report mode (like PowerShell output)
```

### Port Scanning

```bash
# Scan ports (Windows: Test-NetConnection -Port <port>, or nmap)
nmap 192.168.1.0/24                    # Scan subnet
nmap -p 22,80,443 192.168.1.1         # Specific ports
nmap -sV 192.168.1.1                   # Service versions
nmap -O 192.168.1.1                    # OS detection

# Quick port check
ss -tlnp | grep :80                    # What process uses port 80?
lsof -i :80                            # List processes on port 80
netstat -tlnp | grep :80               # Traditional netstat
```

---

## Network Connections

### Active Connections

```bash
# View connections (Windows: Get-NetTCPConnection, netstat -ano)
ss -tlnp                              # Listening TCP sockets
ss -tunp                              # All TCP/UDP connections with PIDs
ss -s                                 # Socket statistics summary
ss -t state established ( sport = :80 or dport = :80 )  # Connections to/from port 80

# Traditional (Windows: netstat -ano)
netstat -tlnp                         # TCP listeners
netstat -an | grep ESTABLISHED        # Established connections
netstat -rn                           # Routing table (like route print)

# Protocol-specific
ss -tuln | grep :53                   # DNS listeners
ss -tuln | grep :22                   # SSH listeners
```

### DNS Resolution

```bash
# DNS (Windows: nslookup, Resolve-DnsName)
dig google.com                        # DNS lookup (most powerful)
dig +short google.com                # Short output (like nslookup)
nslookup google.com                   # Traditional DNS tool
host google.com                       # Quick DNS lookup
cat /etc/hosts                        # Local DNS override (like Windows %windir%\System32\drivers\etc\hosts)
curl ifconfig.me                      # Get external IP (like ipconfig.me or checkip.amazonaws.com)
```

### Network Statistics

```bash
# Network stats (Windows: Get-NetAdapterStatistics, Get-NetTCPConnection)
ss -s                                 # Socket statistics
cat /proc/net/tcp                     # Raw TCP connections (kernel)
cat /proc/net/dev                     # Interface statistics
ethtool eth0                          # Interface details (speed, duplex, etc.)
mii-tool eth0                         # Media access info
```

---

## Routing

### Routing Table

```bash
# Routing (Windows: route print, Get-NetRoute)
ip route show                         # Routing table (modern)
ip route get 8.8.8.8                  # Specific route
ip -6 route show                      # IPv6 routing

# Traditional (Windows: route print)
route -n                              # Numeric routing table
netstat -rn                           # Routing table via netstat

# Add/remove routes (Windows: New-NetRoute, Remove-NetRoute)
sudo ip route add 10.0.0.0/8 via 192.168.1.1   # Add static route
sudo ip route del 10.0.0.0/8 via 192.168.1.1   # Remove static route
```

### ARP Table

```bash
# ARP (Windows: arp -a)
ip neigh show                         # ARP/NDP table
arp -a                                # Traditional ARP table
```

---

## Network Configuration Files

```bash
# Key network config files (Windows: registry + DNS client config)
# /etc/hosts       → Local DNS override (like C:\Windows\System32\drivers\etc\hosts)
# /etc/resolv.conf → DNS servers (like HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters\AdapterServerAddresses)
# /etc/netplan/*   → Network config (Ubuntu)
# /etc/network/interfaces → Network config (Debian classic)
# /etc/nsswitch.conf → Name service switch (DNS, files, winbind order)
```

```bash
# /etc/hosts example (Windows hosts file)
127.0.0.1     localhost
127.0.1.1     ubuntu
192.168.1.100 webserver.local     # Custom hostname entry

# /etc/nsswitch.conf — name resolution order (Windows: registry NetConfig)
# hosts:          files mdns4_minimal [NOTFOUND=return] dns mdns4
# Similar to Windows: DNS → LMhosts → Hosts → WINS → NetBIOS

# /etc/gai.conf — IPv6/IPv4 preference (Windows: DNS client)
# prepend ::1 for IPv6, use for dual-stack ordering
```

---

## Firewall

```bash
# Linux firewall tools (Windows: Windows Defender Firewall / netsh advfirewall)
# Two main firewalls on Linux:
#   1. iptables (legacy, still widely used)
#   2. nftables (modern replacement, iptables is now a compatibility layer)
```

### iptables Basics

```bash
# Firewall rules (Windows: New-NetFirewallRule)
sudo iptables -L -n -v              # List rules (verbose, numeric)
sudo iptables -L -n -v --line-numbers  # With rule numbers
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT  # Allow HTTP
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT # Allow HTTPS
sudo iptables -A INPUT -p tcp --dport 22 -j DROP    # Block SSH
sudo iptables -D INPUT 3             # Delete rule 3
sudo iptables -F                     # Flush all rules (dangerous!)
sudo iptables-save > /etc/iptables.rules  # Save rules
```

### firewalld / ufw

```bash
# UFW (Ubuntu default firewall — simpler than Windows Firewall GUI)
sudo ufw status                       # Check status
sudo ufw enable                       # Enable firewall
sudo ufw default deny incoming        # Default deny all incoming
sudo ufw default allow outgoing       # Allow all outgoing
sudo ufw allow 80/tcp                 # Allow HTTP
sudo ufw allow 443/tcp                # Allow HTTPS
sudo ufw allow ssh                    # Allow SSH (port 22)
sudo ufw delete allow 80/tcp          # Remove rule
sudo ufw reload                       # Reload rules

# Firewalld (RHEL/CentOS/Fedora)
sudo firewall-cmd --list-all          # Current zones
sudo firewall-cmd --add-service=http --permanent  # Allow HTTP
sudo firewall-cmd --add-port=8080/tcp --permanent  # Allow custom port
sudo firewall-cmd --reload            # Apply changes
```

---

## Hands-On Exercise

```bash
# 1. Interface overview
ip -br addr                           # Quick interface view
ip -s link                            # Interface statistics
cat /proc/net/dev                     # Kernel interface stats

# 2. Connectivity
ping -c 4 google.com                  # Basic ping
ping -c 1 -W 2 google.com             # Single ping with timeout
traceroute google.com                 # Trace route
mtr -r google.com                     # Traceroute report mode

# 3. Check listening services
ss -tlnp                              # What's listening?
ss -tuln | grep :22                   # SSH listener
ss -tuln | grep :53                   # DNS listener

# 4. DNS
dig +short google.com                 # DNS resolution
cat /etc/resolv.conf                  # DNS servers
cat /etc/hosts                        # Local DNS overrides

# 5. Routing
ip route show                         # Routing table
ip route get 8.8.8.8                  # Specific route
ip neigh show                         # ARP table

# 6. Network interfaces (hardware)
ethtool eth0                          # Interface details
lspci | grep -i ethernet              # Network hardware

# 7. Firewall
sudo ufw status verbose               # UFW status (if installed)
sudo iptables -L -n -v                # iptables rules

# 8. External IP
curl ifconfig.me                      # Your public IP
```

---

## Mental Model Shift

| Windows Network Mindset | Linux Network Mindset |
|--|--|
| Get-NetAdapter + ipconfig | `ip addr` + `ip link` + `ip -br addr` |
| Set-NetIPAddress | `ip addr add` + `/etc/netplan/` (persistent) |
| Get-NetTCPConnection | `ss -tunp` or `lsof -i` |
| netstat -ano | `ss -tlnp` or `netstat -tlnp` |
| Test-NetConnection | `nc -zv` or `curl` |
| tracert | `traceroute` or `mtr` |
| nslookup / Resolve-DnsName | `dig` or `host` or `nslookup` |
| Get-NetFirewallRule | `iptables -L` or `ufw status` |
| New-NetFirewallRule | `iptables -A` or `ufw allow` |
| netsh advfirewall | `iptables` / `nftables` / `ufw` / `firewalld` |
| Get-NetRoute + route print | `ip route` or `route -n` |
| arp -a | `ip neigh` or `arp -a` |
| Set-DnsClientServerAddress | `/etc/resolv.conf` (direct edit) |
| C:\Windows\System32\drivers\etc\hosts | `/etc/hosts` (same concept, different location) |
| DNS client service (Dnscache) | systemd-resolved + /etc/resolv.conf |
| One tool family (Get-Net*) | Many tools: `ip`, `ss`, `dig`, `nslookup`, `iptables`, `ufw`, `netplan`, `nmcli`, `ethtool` |
| Config via registry/GUI | Config via files: /etc/netplan/, /etc/hosts, /etc/resolv.conf |
| DHCP = automatic | dhclient + netplan config |
| Network Connections GUI | CLI-only (ip, nmcli, netplan) |

**Key takeaway:** Linux networking is **file-driven** — interfaces are configured in `/etc/netplan/` (Ubuntu) or `/etc/network/interfaces` (Debian), DNS in `/etc/resolv.conf`, hosts in `/etc/hosts`. The core commands map to Windows: `ip addr` = ipconfig/Get-NetAdapter, `ss -tlnp` = Get-NetTCPConnection/netstat, `dig` = nslookup/Resolve-DnsName, `ufw`/`iptables` = Windows Defender Firewall. **Unlike Windows where Get-Net* covers everything**, Linux splits networking across many tools: `ip` (interfaces/routing), `ss` (connections), `dig` (DNS), `iptables`/`ufw` (firewall). **Remember**: `ping` in Linux defaults to continuous (use `-c N` for N pings), and **interface config changes are temporary** unless you save to `/etc/netplan/` or `/etc/network/interfaces`. The modern tool is `ip` — `ifconfig` is deprecated. `nftables` is replacing `iptables` but both work. **Always check `ss -s` for socket stats** when debugging network issues.
