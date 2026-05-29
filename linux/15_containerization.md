# Module 15: Containerization & Virtualization

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you manage containers and virtualization through:

```
Windows:
  Docker Desktop for Windows → Docker on WSL2 backend
  docker run --name web -d -p 8080:80 nginx → Same docker commands!
  docker ps / docker logs → Same!
  docker-compose → Same!
  docker build -t myapp . → Same!
  Get-Container → List containers (if using Moby engine)
  Get-VM → List Hyper-V VMs
  New-VHD -Path C:\vms\disk.vhdx -SizeBytes 50GB → Create virtual disk
  Mount-VHD / Dismount-VHD → Attach/detach disks
  Test-VMHeartbeat → Check VM health
  Checkpoint-VM → Snapshots (Windows: VM snapshots)
  Get-VMNetworkAdapter → VM network config
  Get-VMHost → Hyper-V host info
  Enable-Container → Enable Docker (Docker Desktop)
  wsl --install → WSL2 installation
  wsl -l -v → List installed distros
  New-PSSession -ContainerId → Connect to container process
  Get-ContainerNetwork → List networks
  New-VM / Start-VM / Stop-VM → Hyper-V VM management
  Get-VMProcessor → CPU allocation
  Get-VMHardDiskDrive → Disk config
  Set-VMProcessor / Set-VMMemory → Resource limits
  Export-VM / Import-VM → VM migration
  Get-VMIntegrationService → Guest tools status
  Set-VMFirmware → Boot order (UEFI/BIOS)
  Get-VMSwitch → Virtual switch config
  New-VMSwitch → Create virtual switch
  Get-VMNetworkAdapter -VMName web → VM networking
  Test-VM → VM health check
  Get-VMReplication → Hyper-V replication status
  Enable-VMReplication → Enable replication
  Backup-VM → VM backup
  Get-VMConfiguration → VM settings
  Get-VMReplicationRelationship → Replication config
  Get-VMSnapshot → VM snapshots
  Restore-VMSnapshot → Rollback to snapshot
  Get-VMFirmware → Boot config
  Start-VM -Checkpoint → Snapshot then start
  Enable-VMHyperVImport → Import Hyper-V VM
  Get-VMHostFeature → Hyper-V host features
  Checkpoint-VM → VM snapshot (like Docker checkpoint)
```

Windows has **Docker Desktop** (WSL2 backend), **Hyper-V** (native hypervisor), and **WSL2** (Linux subsystem). These map directly to Linux Docker, QEMU/KVM, and WSL. **Docker commands are identical** across platforms — the Linux native backend is just the production standard.

## The Shift

Linux containers use **Docker** (or **Podman**, **Buildah**, **Pod**) for application containerization and **QEMU/KVM** for hardware virtualization. Unlike Windows where Docker Desktop wraps WSL2 (a full Linux VM under the hood), Linux Docker runs directly on the kernel — no VM layer, no Docker Desktop dependency. **Docker commands are identical** across platforms; differences are in installation, service management, and underlying storage drivers. **`systemctl`** replaces `Get-Service` for Docker service control. **`usermod`** replaces Docker Desktop's user-group setup. **`podman`** (rootless, no daemon) is the systemd-free alternative. **`docker-compose`** replaces `New-ContainerNetwork` and multiple `New-Container` commands with a single YAML file.

---

## Docker — Container Management

### Docker Install & Service

```bash
# Docker install & service (Windows: docker run, docker ps — same commands!)
curl -fsSL https://get.docker.com | sh    # Auto-install Docker (Windows: Docker Desktop installer)
sudo usermod -aG docker $USER              # Add user to docker group (Windows: Docker Desktop admin)
newgrp docker                              # Apply group membership (Windows: re-login to Docker Desktop)

# Docker service management (Windows: Docker Desktop tray icon or Get-Service Docker*)
sudo systemctl start docker                # Start Docker (Windows: Docker Desktop starts automatically)
sudo systemctl enable docker               # Auto-start on boot
sudo systemctl status docker               # Check status
sudo systemctl stop docker                 # Stop
sudo systemctl restart docker              # Restart

# Docker info (Windows: docker info — same command!)
docker info                                # Docker daemon info
docker version                             # Client/server versions
docker system df                           # Disk usage (Windows: Docker Desktop settings → Resources)
docker system prune                        # Clean unused data (Windows: Docker Desktop → Discard all)
```

### Container Operations

```bash
# Container lifecycle (Windows: docker run, docker ps — identical commands!)
docker run --name web -d -p 8080:80 nginx              # Run container (Windows: same command!)
docker run --name api -d -p 3000:3000 -e NODE_ENV=prod node:18  # Run with env vars
docker run -it ubuntu bash                             # Interactive container
docker run -d -v data:/var/lib/mysql mysql:8            # With volume mount
docker run -d --network mynet --name db -e MYSQL_ROOT_PASSWORD=pass mysql:8  # Custom network
docker ps                                              # Running containers (Windows: same!)
docker ps -a                                           # All containers (Windows: same!)
docker logs web                                        # Container logs (Windows: same!)
docker logs -f web                                     # Follow logs (Windows: same!)
docker logs --tail 50 web                              # Last 50 lines
docker exec -it web bash                               # Enter container (Windows: same!)
docker exec web uptime                                 # Command in container (Windows: same!)
docker exec -it web sh                                 # Sh shell (Windows: same!)
docker stop web                                        # Stop container (Windows: same!)
docker start web                                       # Start container (Windows: same!)
docker restart web                                     # Restart container (Windows: same!)
docker rm web                                          # Remove container (Windows: same!)
docker rm -f web                                       # Force remove (Windows: same!)
docker prune containers                                # Remove stopped containers (Windows: same!)
docker run --rm -it ubuntu bash                        # Auto-remove on exit
docker run --restart=always --name persistent nginx    # Auto-restart on failure
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE   # Drop all caps, add specific
docker run --security-opt=no-new-privileges              # No privilege escalation
docker run --read-only                                 # Read-only filesystem
docker run --memory=512m --cpus=1                      # Resource limits (Windows: docker run --memory / --cpus)
docker stats                                           # Live container stats (Windows: same!)
docker inspect web                                     # Container details (Windows: same!)
docker port web                                        # Port mappings (Windows: same!)
docker top web                                         # Processes inside (Windows: same!)
docker events                                          # Stream of Docker events (Windows: same!)
```

### Images

```bash
# Image management (Windows: docker images — same command!)
docker images                                          # List images (Windows: same!)
docker pull nginx:latest                               # Pull image (Windows: same!)
docker pull node:18-alpine                             # Pull specific tag
docker rmi nginx                                       # Remove image (Windows: same!)
docker rmi -f nginx                                    # Force remove
docker tag nginx myregistry/nginx:latest               # Tag image
docker push myregistry/nginx:latest                    # Push to registry (Windows: same!)
docker login                                           # Login to registry (Windows: docker login)
docker logout                                          # Logout (Windows: same!)
docker save nginx -o nginx.tar                         # Save image to tar (Windows: same!)
docker load -i nginx.tar                               # Load from tar
docker history nginx                                   # Image layers (Windows: same!)
docker image prune                                     # Remove unused images (Windows: same!)
docker images -aq                                      # All image IDs (Windows: same!)
docker images --filter "dangling=true"                 # Dangling images
docker images -f "reference=*nginx*"                   # Filter by name
```

### Docker Compose

```bash
# Docker Compose (Windows: docker-compose.yml — same file!)
# docker-compose.yml (identical on Windows & Linux):
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
    networks:
      - frontend
    restart: always

  app:
    image: node:18-alpine
    working_dir: /app
    volumes:
      - ./app:/app
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    networks:
      - frontend
      - backend
    depends_on:
      - db

  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: myapp
    volumes:
      - dbdata:/var/lib/mysql
    networks:
      - backend
    restart: always

networks:
  frontend:
  backend:

volumes:
  dbdata:

# Compose commands (Windows: same commands!)
docker-compose up -d                                   # Start all services
docker-compose down                                    # Stop and remove
docker-compose ps                                      # List services
docker-compose logs -f web                             # Follow logs
docker-compose exec web bash                           # Enter container
docker-compose build                                   # Build images
docker-compose pull                                    # Pull images
docker-compose restart web                             # Restart service
docker-compose config                                  # Validate config
docker-compose up -d --build                           # Rebuild and start
```

### Docker Networks

```bash
# Networks (Windows: docker network ls — same commands!)
docker network ls                                      # List networks (Windows: same!)
docker network create mynet                            # Create bridge network (Windows: same!)
docker network inspect mynet                           # Network details (Windows: same!)
docker network rm mynet                                # Remove network
docker network prune                                   # Remove unused networks
docker run --network mynet --name web nginx            # Run on custom network
docker network connect mynet container_name            # Add container to network
docker network disconnect mynet container_name         # Remove from network
```

---

## Podman — Rootless Alternative

```bash
# Podman (Windows: WSL2 Docker Desktop — podman is the rootless alternative to Docker)
sudo apt install podman                                # Install podman (Windows: not available natively, use Docker)
podman run --name web -d -p 8080:80 nginx              # Same as docker run (no daemon!)
podman ps                                              # List containers
podman exec -it web bash                               # Enter container
podman stop web && podman rm web                       # Clean up
podman images                                          # List images
podman pull nginx:latest                               # Pull image
podman rmi nginx                                       # Remove image
podman build -t myapp .                                # Build image
podman system prune                                    # Clean up
podman generate systemd --new --name web > podman-web.service  # Generate systemd unit
# podman replaces docker for rootless, daemonless operation (Windows: Docker Desktop with rootless mode)

# Podman vs Docker (Windows: Docker Desktop vs podman in WSL2)
podman run -d --name web -p 80:80 nginx               # Podman (no daemon needed)
docker run -d --name web -p 80:80 nginx               # Docker (daemon required)
# podman is a drop-in replacement — same CLI, no daemon, runs as root or rootless
```

---

## Container Orchestration & Registry

### Registry & Mirror

```bash
# Docker Registry (Windows: docker registry — same concepts!)
docker run -d -p 5000:5000 --name registry registry:2  # Run local registry
docker tag nginx localhost:5000/nginx                  # Tag for local registry
docker push localhost:5000/nginx                       # Push to local registry
docker pull localhost:5000/nginx                       # Pull from local registry

# Docker mirror (for registry mirrors)
# /etc/docker/daemon.json:
# {
#   "registry-mirrors": ["https://mirror.gcr.io"]
# }
sudo systemctl restart docker                          # Apply mirror config
```

### Container Security

```bash
# Security (Windows: Docker Desktop security settings)
docker run --user 1000:1000 nginx                      # Run as non-root user
docker run --cap-drop=ALL nginx                        # Drop all capabilities
docker run --cap-add=NET_BIND_SERVICE nginx            # Add specific capability
docker run --security-opt=no-new-privileges nginx      # No privilege escalation
docker run --read-only nginx                           # Read-only filesystem
docker run --tmpfs /tmp:size=100m nginx               # Temporary filesystem
docker run --security-profile=sandbox nginx            # Built-in security profile
docker scan nginx                                      # Image vulnerability scan (Trivy)
```

### Container Networking (Windows: Docker Desktop networking)

```bash
# Networking (Windows: docker network commands)
docker network create myapp-net --subnet 172.20.0.0/16  # Create custom network
docker network connect myapp-net web                    # Connect container to network
docker network disconnect myapp-net web                 # Disconnect container
docker network inspect bridge                           # Inspect network
docker network ls                                       # List networks
docker network prune                                    # Remove unused networks
```

### Container Storage & Volumes (Windows: Docker Desktop file sharing)

```bash
# Volumes (Windows: Docker Desktop file sharing → bind mounts)
docker volume create mydata                             # Create named volume
docker volume ls                                        # List volumes
docker volume inspect mydata                            # Volume details
docker volume rm mydata                                 # Remove volume
docker run -v mydata:/data nginx                        # Mount named volume
docker run -v /host/path:/container/path nginx          # Bind mount
docker run --tmpfs /tmp:size=100m nginx                 # Temporary filesystem
```

### Container Health & Monitoring

```bash
# Health checks (Windows: Docker Desktop monitoring)
docker run -d --name web --health-cmd="curl -f http://localhost || exit 1" --health-interval=30s nginx  # Health check
docker inspect --format='{{.State.Health.Status}}' web  # Check health
docker stats                                            # Live stats
docker top web                                          # Container processes
```

### Container Lifecycle

```bash
# Lifecycle management (Windows: Docker Desktop lifecycle)
docker run -d --name web --restart=always nginx         # Auto-restart on failure
docker run -d --name web --restart=on-failure:3 nginx   # Restart on failure (max 3)
docker update --restart=unless-stopped web              # Update restart policy
docker pause web                                        # Pause container
docker unpause web                                      # Unpause
docker wait web                                         # Wait for stop
docker export web > container.tar                       # Export filesystem
docker import container.tar myimage                     # Import as image
```

---

## QEMU/KVM — Hardware Virtualization

### KVM Setup & VM Management

```bash
# KVM setup (Windows: Hyper-V Manager)
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager  # Install KVM
sudo adduser $USER libvirt                              # Add user to libvirt group
sudo systemctl enable --now libvirtd                    # Start libvirt service
sudo systemctl status libvirtd                          # Check service

# VM management (Windows: New-VM, Start-VM, Get-VM — KVM uses different CLI)
virsh list                                              # List running VMs (Windows: Get-VM)
virsh list --all                                        # List all VMs (Windows: Get-VM -All)
virsh start web                                         # Start VM (Windows: Start-VM)
virsh shutdown web                                      # Shutdown VM (Windows: Stop-VM)
virsh destroy web                                       # Force power off (Windows: Stop-VM -TurnOff)
virsh suspend web                                       # Suspend VM (Windows: Suspend-VM)
virsh resume web                                        # Resume VM (Windows: Resume-VM)
virsh reboot web                                        # Reboot VM (Windows: Restart-VM)
virsh undefine web                                      # Remove VM config (Windows: Remove-VM)
virsh autostart web                                     # Auto-start on boot (Windows: Set-VM -AutomaticStartAction Start)
virsh dumpxml web > web.xml                             # Export VM config
virsh define web.xml                                    # Import VM config
virsh rename web new-web                                # Rename VM

# VM resources (Windows: Set-VMProcessor, Set-VMMemory)
virsh vcpus web 4                                       # Set CPU cores
virsh setmem web 2GB                                    # Set memory
virsh dominfo web                                       # VM info
virsh domblklist web                                    # Disk devices
virsh domiflist web                                     # Network devices

# VM snapshots (Windows: Checkpoint-VM)
virsh snapshot-create web                               # Create snapshot
virsh snapshot-list web                                 # List snapshots
virsh snapshot-revert web snapshot1                     # Revert to snapshot
virsh snapshot-delete web snapshot1                     # Delete snapshot

# Disk management (Windows: New-VHD, Mount-VHD)
qemu-img create -f qcow2 web.qcow2 50G                 # Create virtual disk (Windows: New-VHD)
qemu-img info web.qcow2                                 # Check disk info
qemu-img convert -f qcow2 -O raw web.qcow2 web.raw      # Convert format
qemu-img resize web.qcow2 +10G                          # Resize disk

# Network (Windows: New-VMSwitch, Get-VMNetworkAdapter)
virsh net-list                                          # List networks
virsh net-dumpxml default                               # Network config
virsh net-start default                                 # Start network
virsh net-destroy default                               # Destroy network
virsh net-autostart default                             # Auto-start network

# VM creation (Windows: New-VM)
virt-install --name web --ram 2048 --vcpus 2 --disk path=web.qcow2,size=20 --network network=default --cdrom ubuntu.iso --graphics none  # Headless install
virt-install --name web --ram 2048 --vcpus 2 --disk path=web.qcow2,size=20 --network network=default --import --graphics vnc  # Import existing disk
```

### Virt-Manager (GUI for KVM)

```bash
# Virt-Manager (Windows: Hyper-V Manager)
virt-manager                                            # Launch GUI (Windows: virtmgmt.msc)
# Same features as Hyper-V Manager:
# - Create/manage VMs
# - VM snapshots
# - Network config
# - Storage pools
# - Console access
```

### libvirt — Management API

```bash
# libvirt (Windows: Hyper-V PowerShell module)
virsh pool-list                                         # List storage pools
virsh pool-create-as data dir /var/lib/libvirt/data     # Create storage pool
virsh pool-start data                                   # Start pool
virsh pool-autostart data                               # Auto-start pool
virsh vol-create-as data vol1 10G --format qcow2        # Create volume in pool
virsh vol-download vol1 file                            # Download volume

# VM templates (Windows: VM export/import)
virt-clone --original web --name web-copy --auto-clone   # Clone VM
virt-xml web --edit                                     # Edit VM config
virsh dumpxml web > web.xml                             # Export config
virsh define web.xml                                    # Import config
```

---

## LXC/LXD — System Containers

```bash
# LXD (Windows: Docker containers for apps, Hyper-V VMs for full isolation)
sudo apt install lxd                                    # Install LXD
sudo lxd init                                           # Initialize (auto-config for most cases)
lxc launch ubuntu:22.04 web                             # Launch container
lxc exec web bash                                       # Enter container
lxc list                                                # List containers
lxc stop web && lxc delete web                          # Remove
lxc launch ubuntu:22.04 web --profile default           # With profile
lxc config set web security.privileged true             # Privileged container
lxc config device add web disk disk source=/dev/sdb pool=default  # Add disk
lxc profile create myprofile                            # Create profile
lxc profile edit myprofile                              # Edit profile
lxc profile copy default myprofile                      # Copy profile
lxc snapshot web before-update                          # Create snapshot
lxc restore web before-update                           # Restore snapshot
```

---

## Hands-On Exercise

```bash
# 1. Docker basics
docker run --name web -d -p 8080:80 nginx
docker ps
docker logs web
docker exec -it web bash
exit
docker stop web
docker rm web

# 2. Docker Compose
# docker-compose.yml (save in directory):
# version: '3.8'
# services:
#   web:
#     image: nginx:latest
#     ports:
#       - "8080:80"
#     volumes:
#       - ./html:/usr/share/nginx/html
#   db:
#     image: mysql:8
#     environment:
#       MYSQL_ROOT_PASSWORD: pass
#     volumes:
#       - dbdata:/var/lib/mysql
# volumes:
#   dbdata:

docker-compose up -d
docker-compose ps
docker-compose logs -f web
docker-compose down

# 3. Podman (rootless)
podman run --name web -d -p 8081:80 nginx
podman ps
podman stop web && podman rm web

# 4. KVM
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager
sudo adduser $USER libvirt
virsh list --all
virsh net-list

# 5. LXD
sudo apt install lxd
sudo lxd init
lxc launch ubuntu:22.04 web
lxc exec web bash
exit
lxc list
lxc stop web && lxc delete web
```

---

## Mental Model Shift

| Windows Containerization Mindset | Linux Containerization Mindset |
|--|--|
| Docker Desktop (WSL2 backend) → GUI app with Linux VM | Docker → native Linux daemon (dockerd, no VM layer) |
| Docker Desktop tray icon for start/stop | systemctl start/stop docker |
| docker run --name web -d -p 8080:80 nginx | **Same docker command!** (Linux native) |
| docker ps, docker logs, docker exec | **Same commands!** |
| docker-compose.yml | **Same compose file!** |
| Docker Desktop → default bridge network | docker network ls → default bridge (same) |
| Docker Desktop → default named volume | docker volume ls → default local (same) |
| Docker Desktop → settings for resources | /etc/docker/daemon.json (same config format) |
| Docker Desktop → file sharing from Windows dirs | docker run -v /c/Users:/host (bind mount Windows dirs) |
| Get-Container / Get-ContainerNetwork | docker ps / docker network ls |
| New-ContainerNetwork → docker network create | **Same docker command!** |
| New-Container → docker run | **Same docker command!** |
| Docker Desktop → port forwarding config | -p flag in docker run (same) |
| Docker Desktop → volume mapping in settings | -v flag in docker run (same) |
| docker run --restart=always | **Same!** (daemon handles restart) |
| docker run --memory / --cpus | **Same!** |
| docker run --user 1000:1000 | **Same!** |
| Docker Desktop → security profiles | docker run --security-opt (same) |
| Docker Desktop → registry login | docker login (same) |
| Docker Desktop → image management | docker images / docker pull / docker rmi (same) |
| Get-VM → Hyper-V VM management | virsh list / virsh start / virsh shutdown (different!) |
| New-VHD → VHDX virtual disk | qemu-img create -f qcow2 (different!) |
| Checkpoint-VM → VM snapshots | virsh snapshot-create / list / revert |
| Get-VMNetworkAdapter → VM networking | virsh domiflist / net-list (different!) |
| Set-VMProcessor → CPU allocation | virsh vcpus / setmem (different!) |
| Enable-VMReplication → Hyper-V replication | virsh blkcopy / lxc snapshot (different approach) |
| Get-VMReplicationRelationship | virsh pool-list / pool-create-as (storage pools) |
| New-VMSwitch → virtual switch | virsh net-list / net-create (libvirt networks) |
| Start-VM -Checkpoint → snapshot then start | virt-clone → VM cloning (different) |
| Enable-VMHyperVImport → import VM | virsh define xml → import from config (different!) |
| Get-VMHostFeature → Hyper-V features | cat /sys/module/kvm/version → KVM loaded |
| Docker Desktop → VM for Linux kernel | Docker → native Linux (no VM, lighter) |
| Hyper-V → Windows-first hypervisor | KVM → Linux-native hypervisor (integrated in kernel) |
| VM → VHDX disks | VM → QCOW2 disks (qemu-img) |
| VM → dynamically expanding VHDX | VM → QCOW2 (same, but different tool) |
| Hyper-V → nested virtualization | KVM → nested virtualization (CPU flags) |
| Docker Desktop → WSL2 distro management | wsl -l -v → installed distros (WSL, not Docker) |
| Docker Desktop → Kubernetes integration | kubectl → K8s CLI (same, just install) |
| Docker Desktop → container logs in UI | docker logs -f → terminal (same command) |
| Docker Desktop → container file explorer | docker exec -it /bin/sh → ls -la (same) |
| Docker Desktop → resource limits slider | docker run --memory/--cpus → CLI flags (same) |
| Docker Desktop → registry credentials in Windows CM | docker login → ~/.docker/config.json (same) |
| Docker Desktop → auto-update images | docker image prune → manual cleanup (different) |
| Hyper-V Manager → GUI for VMs | virt-manager → GUI for KVM VMs (similar GUI) |
| Hyper-V Manager → quick create VMs | lxc launch ubuntu:22.04 → instant container (faster) |
| Hyper-V → full VM (emulated hardware) | KVM → near-native performance (paravirtualized) |
| WSL2 → full Linux VM inside Windows | WSL → native Linux on Linux (no virtualization layer) |
| Docker Desktop → single Docker engine | Podman → daemonless containers (rootless) |
| Docker Desktop → multi-host networking | Podman → machine (VM-based multi-host) |
| Docker Desktop → Kubernetes cluster | Podman → podman system service (daemonless) |
| Hyper-V → Windows VM management | LXD → system containers (VM-like, Docker-like) |
| Hyper-V → Linux VMs via virtio drivers | LXD → native Linux isolation (lighter than VM) |
| Hyper-V → nested VMs in Linux VM | LXD → nested containers (containers in containers) |
| Docker Desktop → WSL2 distro auto-management | wsl --install → manual distro install (different) |
| Docker Desktop → integration with Visual Studio | VS Code → Remote - Container (same extension) |
| Docker Desktop → integration with VS | VS Code → Dev Containers (same extension) |
| Docker Desktop → integration with VS Code | VS Code → Dev Containers (same) |
| Docker Desktop → WSL2 → Linux kernel | Docker native → direct Linux kernel (no WSL2) |
| Docker Desktop → Hyper-V isolation mode | Docker rootless → user namespaces (no root) |
| Docker Desktop → Linux containers on Windows | WSL2 → Linux kernel in VM (Windows running Linux) |
| Docker Desktop → Windows containers on Linux | Not available (Docker only runs Linux containers on Linux) |
| WSL2 → full Linux distro in VM | WSLg → GUI apps in WSL2 (X11/Wayland) |
| WSL2 → Linux GUI apps in Windows | WSLg → same (X11 forwarding built-in) |
| WSL2 → interoperability (Windows .exe from WSL) | WSLg → same (call Windows apps from WSL) |
| WSL2 → file system access to Windows dirs | WSLg → /mnt/c/ for Windows access (same path) |
| Docker Desktop → Linux containers on Windows | Native Docker → Linux containers on Linux (no shim) |
| Docker Desktop → performance overhead of WSL2 | Docker native → near-native performance (direct kernel) |
| Docker Desktop → 2-4GB RAM overhead for WSL2 | Docker native → ~100MB RAM (no VM overhead) |
| Docker Desktop → slower I/O (cross-VM filesystem) | Docker native → direct filesystem (no cross-boundary) |
| Docker Desktop → larger disk footprint | Docker native → smaller footprint (no extra VM) |
| Docker Desktop → update via Windows Update | Docker → apt update && apt install (same package manager) |
| Hyper-V → VMs visible in Task Manager | KVM → VMs in virsh list (CLI tool) |
| Hyper-V → RAM/CPU sliders in GUI | KVM → virt-install / virsh setmem (CLI) |
| Hyper-V → automatic checkpoint scheduling | LXD → lxc snapshot (manual snapshots) |
| Docker Desktop → built-in Kubernetes (minikube) | k3s / minikube → lightweight K8s (CLI install) |
| Docker Desktop → integrated container registry | Docker Hub → registry (cloud, not built-in) |
| Docker Desktop → container dashboard UI | Portainer / ctop → third-party dashboards |
| Docker Desktop → WSL2 resource config in settings | /etc/docker/daemon.json → daemon config |
| Docker Desktop → automatic WSL2 distro updates | apt upgrade → manual updates (different) |
| Hyper-V → VM export/import as .vmcx/.vmrs | virsh dumpxml/export → XML config (different format) |
| Hyper-V → replication to another host | lxd copy / virsh migrate → live migration (different) |
| Docker Desktop → container networking via NAT | Docker native → native bridge (no NAT needed) |
| Docker Desktop → Windows host networking | Docker → host networking (--network host) |
| Docker Desktop → Windows named pipes for Docker | Docker native → /var/run/docker.sock |
| Docker Desktop → Windows process explorer for containers | docker top / htop → container process view |
| Docker Desktop → container startup logs in UI | journalctl -u docker → systemd logs |
| Docker Desktop → WSL2 distro version updates | wsl --update → WSL2 kernel updates |
| Docker Desktop → WSL2 automatic memory management | cgroups v2 → Linux memory management |
| Docker Desktop → WSL2 automatic disk management | lvm/luks → Linux storage management |
| Hyper-V → guest services integration | KVM guest tools → virtio drivers (similar concept) |
| Hyper-V → time sync with host | KVM → same time sync (kvmclock) |
| Docker Desktop → integrated terminal (PowerShell + WSL) | Terminal → GNOME Terminal / Terminator (separate) |
| Docker Desktop → WSL2 distro as "container runtime" | Docker daemon → native container runtime (runc) |

**Key takeaway:** Docker commands (`docker run`, `docker ps`, `docker-compose`) are **identical** across Windows and Linux — the container files and commands you write on Windows work identically on Linux. The main difference is **installation**: Windows uses Docker Desktop (GUI app wrapping WSL2), while Linux uses `apt install docker.io` (native daemon). **Docker daemon** runs as `systemctl` service (not a tray icon). For VMs, Linux uses **QEMU/KVM** (`virsh` CLI, `virt-manager` GUI) instead of Hyper-V — different tools but same concepts. **Podman** is the rootless daemonless alternative to Docker (no systemctl needed). **LXD** provides system containers (VM-like isolation, Docker-like UX). **No Docker Desktop dependency** on Linux — lighter weight, better performance, direct kernel access.
