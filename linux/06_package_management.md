# Module 6: Package Management

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage software installation through:

```
Windows Package Management:
  winget install Microsoft.PowerToys     # Modern package manager
  choco install git                       # Chocolatey (community)
  scoop install curl                      # Scoop (community)
  msiexec /i software.msi                 # MSI installers
  WSUS (Windows Server Update Services)   # Enterprise patch management
  Group Policy Software Installation       # GPO-based deployment
  \\server\share\setup.exe /quiet         # Manual silent install
```

Windows uses **MSI packages** or **chocolatey/scoop** as package managers. WSUS handles OS patches. `winget` is the modern unified tool.

## The Shift

Linux uses **distribution-specific package managers** (apt, yum/dnf, pacman, zypper, etc.) with **package repositories** (remote servers). There's no "universal" package manager — each distro picks one.

```bash
# Windows: one tool (winget/choco) covers everything
# Linux: each distro has its own manager

Ubuntu/Debian → apt / apt-get
RHEL/CentOS/Fedora → dnf (yum)
openSUSE → zypper
Arch → pacman
Gentoo → emerge
Alpine → apk
```

### apt — The Ubuntu/Debian Package Manager

```bash
# Update package list (Windows: winget upgrade --all / WSUS sync)
sudo apt update                     # Refresh repository metadata
sudo apt upgrade                    # Upgrade all installed packages
sudo apt full-upgrade               # Upgrade + remove obsolete packages (recommended)

# Install a package (Windows: winget install git)
sudo apt install git                # Install git
sudo apt install nginx              # Install nginx
sudo apt install htop curl jq       # Install multiple packages
sudo apt install --no-install-recommends git   # Install without "recommended" extras

# Remove a package (Windows: winget uninstall git / choco uninstall git)
sudo apt remove git                 # Remove package, keep config files
sudo apt purge git                  # Remove package AND config files
sudo apt autoremove                 # Remove unused dependencies
sudo apt clean                      # Remove downloaded .deb files

# Search for a package (Windows: winget search nginx)
apt search nginx                    # Search by name
apt-cache search nginx              # Search description
apt show nginx                      # Show package details
apt-file search filename            # Find which package owns a file (install apt-file first)

# List installed packages (Windows: winget list)
dpkg --list                         # All installed packages
dpkg -l | grep nginx                # Filter by name
apt list --installed                # List installed packages (apt-specific)
apt list --upgradable               # List upgradable packages

# Reinstall a package (Windows: winget repair / winget reinstall)
sudo apt install --reinstall nginx

# Download a package without installing (Windows: winget download)
apt download nginx                  # Download .deb to current directory
dpkg --contents nginx.deb           # List .deb contents
```

### dnf / yum — The RHEL/CentOS/Fedora Package Manager

```bash
# Update package list
sudo dnf check-update               # Check for updates
sudo dnf update                     # Upgrade all packages

# Install a package (Windows: winget install git)
sudo dnf install git
sudo dnf install nginx httpd-tools  # Install multiple packages

# Remove a package
sudo dnf remove git
sudo dnf autoremove                 # Remove unused dependencies

# Search for a package (Windows: winget search nginx)
dnf search nginx                    # Search by name
dnf info nginx                      # Show package details

# List installed packages
dnf list installed                  # All installed packages
dnf list installed | grep nginx     # Filter by name

# Reinstall
sudo dnf reinstall nginx

# Download a package
dnf download nginx                  # Download RPM to current directory
rpm -qpl nginx.rpm                  # List RPM contents
```

### Package Repository Files

```bash
# Repositories (Windows: winget source / WSUS server)
# Where packages come from (Windows: winget source list / WSUS config)

# Ubuntu/Debian repositories (Windows: WSUS server configuration)
cat /etc/apt/sources.list           # Main repository list (older Ubuntu)
ls /etc/apt/sources.list.d/         # Additional repository files
apt-cache policy nginx              # Show which repo nginx comes from
apt-cache policy                    # Show all configured repositories

# Add a PPA (Personal Package Archive) — like a private winget source (Windows: winget source add)
sudo add-apt-repository ppa:ondrej/php
sudo apt update                     # Refresh after adding PPA

# Remove a PPA
sudo add-apt-repository --remove ppa:ondrej/php
sudo apt update

# Pin specific package versions (Windows: winget install --version 1.0)
# /etc/apt/preferences.d/pin-version   # Pin to specific version
```

### Managing Packages — Common Operations

```bash
# Find what owns a file (Windows: Get-AppxPackage | Select-Object -ExpandProperty PackageFullName)
dpkg -S /usr/bin/git                # Which package installed git?
dpkg -L nginx                       # List all files installed by nginx
rpm -qf /usr/bin/git                # RHEL/CentOS equivalent

# Check if a package is installed (Windows: winget show nginx)
dpkg -l | grep nginx               # Ubuntu/Debian
dpkg -s nginx                       # Show package status (installed/pending)
dpkg -L nginx                       # List installed files
rpm -q nginx                        # RHEL/CentOS check

# List what a package would install
apt-cache depends nginx             # Dependencies
apt-cache rdepends nginx            # Reverse dependencies (what needs nginx?)
apt-cache depends git | grep Depends  # What git needs

# Clean up (Windows: winget repair / choco clean)
sudo apt autoremove                 # Remove orphaned dependencies
sudo apt clean                      # Clear /var/cache/apt/*.deb
sudo apt autoclean                  # Remove old cached .deb files
df -h                               # Check disk space after cleanup
```

### Third-Party & Non-Repos

```bash
# Installing .deb packages (Windows: msiexec /i package.msi)
dpkg -i package.deb                 # Install a .deb file
dpkg --configure -a                 # Fix broken installs
apt-get install -f                  # Fix broken dependencies

# Installing .rpm packages (Windows: msiexec /i)
rpm -ivh package.rpm                # Install RPM
rpm -Uvh package.rpm                # Upgrade RPM
rpm -qpl package.rpm                # List RPM contents
rpm -qpf package.rpm                # Show RPM info

# Snap packages (universal, Windows Store-style)
snap list                           # Installed snaps
snap install core                    # Install a snap
snap refresh                        # Update all snaps
snap remove core                    # Remove a snap

# Flatpak packages (universal, winget Store-style)
flatpak list                        # Installed flatpaks
flatpak install flathub org.gimp.GIMP   # Install from Flathub
flatpak update                      # Update all flatpaks
flatpak uninstall org.gimp.GIMP     # Remove a flatpak

# APT — for non-repos
wget https://example.com/app.deb
sudo apt install ./app.deb          # Install from local .deb (includes deps)
```

### Service & System Management

```bash
# Enable/disable services (Windows: Set-Service nginx -StartupType Automatic)
systemctl is-enabled nginx          # Is it enabled at boot?
sudo systemctl enable nginx         # Enable at boot
sudo systemctl disable nginx        # Disable at boot
sudo systemctl start nginx          # Start now
sudo systemctl stop nginx           # Stop now
sudo systemctl restart nginx        # Restart
sudo systemctl reload nginx         # Reload config (no downtime)
sudo systemctl status nginx         # Current status
```

### Package Manager Comparison

| Task | Ubuntu/Debian (apt) | RHEL/Fedora (dnf) | Windows (winget) |
|------|------|------|------|
| Update metadata | `apt update` | `dnf check-update` | `winget upgrade --all` |
| Install package | `apt install git` | `dnf install git` | `winget install git` |
| Remove package | `apt remove git` | `dnf remove git` | `winget uninstall git` |
| List installed | `dpkg -l` | `dnf list installed` | `winget list` |
| Search package | `apt search nginx` | `dnf search nginx` | `winget search nginx` |
| Package details | `apt show nginx` | `dnf info nginx` | `winget show nginx` |
| Fix broken | `apt-get install -f` | `dnf distro-sync` | `winget repair` |
| Clean cache | `apt clean` | `dnf clean all` | `winget clean` |
| Repo list | `/etc/apt/sources.list` | `/etc/yum.repos.d/` | `winget source list` |
| PPA | `add-apt-repository ppa:` | COPR repos | `winget source add` |

## Hands-On Exercise

```bash
# 1. Update your package manager
sudo apt update
sudo apt upgrade -y

# 2. Install common tools
sudo apt install -y htop curl jq strace tcpdump

# 3. Check if tools are installed
dpkg -l | grep -E 'htop|curl|jq'
which htop curl jq

# 4. Search for a package
apt search web server | head -20
apt-cache search nginx

# 5. Get package details
apt show nginx | head -30
dpkg -s nginx                           # Check if installed
dpkg -L nginx                           # List its files

# 6. Clean up
sudo apt autoremove -y
sudo apt clean
df -h                                   # Check freed space

# 7. Explore the repos
cat /etc/apt/sources.list
ls /etc/apt/sources.list.d/
apt-cache policy nginx                  # Where would nginx come from?

# 8. List all installed packages (count them)
dpkg -l | grep '^ii' | wc -l

# 9. Find what owns a file
dpkg -S /usr/bin/ssh
dpkg -S /usr/bin/nginx

# 10. Install nginx, check status, clean up
sudo apt install -y nginx
systemctl is-enabled nginx
sudo apt remove --purge nginx
sudo apt autoremove -y
```

## Mental Model Shift

| Windows Package Management | Linux Package Management |
|--|--|
| winget install git | `apt install git` |
| winget uninstall git | `apt remove git` |
| winget list | `dpkg -l` |
| Winget Source / WSUS server | `/etc/apt/sources.list` + `/etc/apt/sources.list.d/` |
| MSI installer (msiexec) | .deb / .rpm files (`dpkg -i`) |
| Chocolatey / Scoop | Snap / Flatpak (universal packages) |
| Add-Computer / Domain join | add-apt-repository (repo join) |
| winget upgrade --all | apt full-upgrade / dnf update |
| Package = .exe or .msi | Package = compiled binaries + config + deps |
| Silent install flags (/quiet, /norestart) | apt install -y (yes to all) |
| Add-Content to sources.json | add-apt-repository ppa: |
| Remove-Content from sources.json | add-apt-repository --remove ppa: |
| wsusutil config | /etc/apt/preferences.d/ (pinning) |
| Package = application | Package = application + dependencies + config |
| One manager (winget) covers all | Different manager per distro (apt, dnf, pacman) |
| App is AppX or Win32 | App is snap, flatpak, or native package |

**Key takeaway:** Linux packages are **distro-specific** — Ubuntu uses `apt`, RHEL uses `dnf`, Arch uses `pacman`. The most common commands are `apt update` → `apt install` → `apt remove` → `apt autoremove`. Unlike Windows where "uninstall" removes the app, on Linux `apt remove` keeps config files — use `apt purge` to remove them too. `apt full-upgrade` is preferred over `apt upgrade` because it handles dependency changes. Always `apt update` before installing. Service management uses `systemctl enable/start/stop`. For non-repo packages, use `.deb`/`.rpm` files or snap/flatpak universal packages.
