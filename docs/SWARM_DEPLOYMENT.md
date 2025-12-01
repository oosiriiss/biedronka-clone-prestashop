# Docker Swarm Deployment Guide

## Overview

This project supports **two deployment modes**:

1. **Development mode** (`docker-compose up`) - Hot reload, easy debugging, single instance
2. **Production/Cluster mode** (`docker stack deploy`) - Swarm orchestration, load balancing, high availability

Both modes use the **same `docker-compose.yml` file** for clean code.

---

## Development Mode (Recommended for Daily Work)

### Quick Start

```powershell
cd docker

# Start services (hot reload enabled)
docker-compose up -d

# View logs
docker-compose logs -f prestashop

# Stop services
docker-compose down
```

### Features

✅ **Hot reload** - changes to `src/themes/biedronka/` immediately visible  
✅ **Fast startup** - single replica, no orchestration overhead  
✅ **Easy debugging** - direct container access, simple logs  
✅ **Volume mounts** - source code mounted from host

### When to Use

- Daily development
- Testing theme changes
- Debugging issues
- Local testing before commit

---

## Production/Cluster Mode (For Deployment Requirements)

### Overview

Deploy the shop in a Docker Swarm cluster with shared database and load balancing to meet project requirements.

### Architecture

```
┌─────────────────────────────────────────┐
│         Docker Swarm Cluster            │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ PrestaShop   │    │ PrestaShop   │  │
│  │ Replica 1    │    │ Replica 2    │  │
│  └──────┬───────┘    └──────┬───────┘  │
│         │                   │          │
│         └─────────┬─────────┘          │
│                   │                    │
│          ┌────────▼────────┐           │
│          │     MySQL       │           │
│          │  Shared DB      │           │
│          └─────────────────┘           │
│                                         │
│  Network: prestashop_network (overlay) │
└─────────────────────────────────────────┘
```

### Key Features

- **Cluster deployment**: Docker Swarm orchestration
- **Shared database**: Single MySQL instance accessible to all PrestaShop replicas
- **Load balancing**: 2 PrestaShop replicas with automatic traffic distribution
- **High availability**: Auto-restart on failure, rolling updates
- **Overlay networking**: Secure multi-host communication
- **Hot reload**: Volume mounts work on single-node clusters

---

## Prerequisites

- Docker Engine 20.10+ with Swarm mode support
- Windows PowerShell or Linux/macOS terminal

---

## Prerequisites

- Docker Engine 20.10+ with Swarm mode support
- Windows PowerShell 5.1+ or Linux/macOS Bash
- At least 4GB RAM available
- Ports 80, 443, 8080 available

---

## Production Mode - Quick Start

### Option A: Automated Deployment (Recommended)

**Windows PowerShell:**

```powershell
.\scripts\deploy-swarm.ps1 -Action deploy
```

**Linux/macOS:**

```bash
chmod +x scripts/deploy-swarm.sh
./scripts/deploy-swarm.sh deploy
```

The script will automatically:

- Initialize Docker Swarm
- Build MySQL and PrestaShop images
- Deploy the stack
- Run deployment tests

### Option B: Manual Deployment

### 1. Initialize Docker Swarm

```bash
# Initialize Swarm mode (creates a single-node cluster)
docker swarm init

# Verify cluster status
docker node ls
```

**Expected output:**

```
ID                            HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
abc123def456 *                DESKTOP    Ready     Active         Leader
```

✅ You now have a Docker Swarm cluster running on localhost.

---

### 2. Build Docker Images

Before deploying the stack, build the required images:

```powershell
cd docker

# Build MySQL image
docker build -t biedronka-mysql:latest -f mysql/Dockerfile ..

# Build PrestaShop image
docker build -t biedronka-prestashop:latest -f prestashop/Dockerfile ..

# Verify images
docker images | Select-String "biedronka"
```

---

### 3. Deploy the Stack

```powershell
# Deploy the entire stack (MySQL + PrestaShop)
docker stack deploy -c docker-compose.yml biedronka

# Verify stack deployment
docker stack ls
docker stack services biedronka
```

**Expected output:**

```
NAME                      REPLICAS   IMAGE                           PORTS
biedronka_mysql           1/1        biedronka-mysql:latest
biedronka_prestashop      2/2        biedronka-prestashop:latest     *:8080->80/tcp, *:443->443/tcp
```

---

## Switching Between Modes

### From Development to Production

```powershell
# 1. Stop compose
docker-compose down

# 2. Init Swarm (if not already done)
docker swarm init

# 3. Build images
docker build -t biedronka-mysql:latest -f mysql/Dockerfile ..
docker build -t biedronka-prestashop:latest -f prestashop/Dockerfile ..

# 4. Deploy stack
docker stack deploy -c docker-compose.yml biedronka
```

### From Production to Development

```powershell
# 1. Remove stack
docker stack rm biedronka

# 2. Leave Swarm (optional - keeps Swarm initialized)
# docker swarm leave --force

# 3. Start compose
docker-compose up -d
```

---

## Comparison: Development vs Production

| Feature                       | Development (`compose`) | Production (`stack`)           |
| ----------------------------- | ----------------------- | ------------------------------ |
| **Hot reload**                | ✅ Yes                  | ✅ Yes (single-node)           |
| **Startup time**              | Fast (~30s)             | Slower (~60s)                  |
| **Replicas**                  | 1 PrestaShop            | 2 PrestaShop (scalable)        |
| **Load balancing**            | ❌ No                   | ✅ Yes                         |
| **Auto-restart**              | ✅ Yes                  | ✅ Yes (advanced)              |
| **Logs**                      | `docker-compose logs`   | `docker service logs`          |
| **Cache clear**               | `docker-compose exec`   | `docker exec $(docker ps ...)` |
| **Meets cluster requirement** | ❌ No                   | ✅ Yes                         |

---

## Daily Development Workflow

### Edit Theme Files (Hot Reload)

```powershell
# 1. Start environment (if not running)
docker-compose up -d

# 2. Edit theme files
code src/themes/biedronka/templates/

# 3. Refresh browser - changes visible immediately! ✅

# 4. View logs if needed
docker-compose logs -f prestashop

# 5. Clear cache if needed
docker-compose exec prestashop php bin/console cache:clear
```

### Test Before Commit (Cluster Validation)

```powershell
# 1. Stop dev environment
docker-compose down

# 2. Deploy to Swarm
docker swarm init  # if not already done
docker build -t biedronka-mysql:latest -f mysql/Dockerfile ..
docker build -t biedronka-prestashop:latest -f prestashop/Dockerfile ..
docker stack deploy -c docker-compose.yml biedronka

# 3. Test cluster functionality
docker service ls
curl http://localhost:8080

# 4. If OK - commit changes
git add .
git commit -m "Feature complete"

# 5. Return to dev mode
docker stack rm biedronka
docker-compose up -d
```

---

## Production Mode - Detailed Guide

### Monitor Deployment

```powershell
# Watch service startup (wait until all replicas are running)
docker service ls

# Check PrestaShop logs
docker service logs biedronka_prestashop -f

# Check MySQL logs
docker service logs biedronka_mysql -f

# List all containers in the stack
docker stack ps biedronka
```

Wait until you see:

- MySQL: `ready for connections`
- PrestaShop: `Apache/2.x.x configured` or `NOTICE: ready to handle connections`

---

### 5. Verify Cluster Deployment

#### Test 1: Database Connection Stability

```powershell
# Get a running PrestaShop container ID
$containerID = (docker ps -q -f name=biedronka_prestashop | Select-Object -First 1)

# Test database connection from inside container
docker exec $containerID php -r "new PDO('mysql:host=mysql;dbname=prestashop', 'root', 'toor'); echo 'DB Connection: OK';"
```

**Expected:** `DB Connection: OK`

#### Test 2: Web Interface

Open browser:

- **HTTPS:** https://localhost (accept self-signed certificate)
- **HTTP:** http://localhost:8080

**Verify:**

- ✅ Homepage loads
- ✅ Products are visible
- ✅ Add to cart works
- ✅ Checkout process works

#### Test 3: Back Office

1. Navigate to: http://localhost:8080/admin-dev
2. Login:
   - Email: `makajler@szpont.pl`
   - Password: `password`
3. Verify:
   - ✅ Dashboard loads
   - ✅ Can add products
   - ✅ Can view orders
   - ✅ Can manage customers

---

## Scaling

### Scale PrestaShop Replicas

```powershell
# Scale up to 3 replicas
docker service scale biedronka_prestashop=3

# Scale down to 1 replica
docker service scale biedronka_prestashop=1

# Verify scaling
docker service ps biedronka_prestashop
```

Docker Swarm automatically load-balances traffic across all replicas.

### Test Load Balancing

```powershell
# Make multiple requests and observe different container IDs in logs
for ($i=1; $i -le 10; $i++) {
    curl http://localhost:8080 -UseBasicParsing | Out-Null
    Write-Host "Request $i sent"
}

# Check logs - should see requests distributed across replicas
docker service logs biedronka_prestashop --tail 20
```

---

## Updates & Rollbacks

### Update PrestaShop Image

```powershell
# Rebuild image with changes
docker build -t biedronka-prestashop:latest -f prestashop/Dockerfile ..

# Update service (rolling update - zero downtime)
docker service update --image biedronka-prestashop:latest biedronka_prestashop
```

### Rollback

```powershell
# Rollback to previous version
docker service rollback biedronka_prestashop
```

---

## Maintenance

### View Stack Resources

```powershell
# List all stacks
docker stack ls

# List services in stack
docker stack services biedronka

# List tasks (containers) in stack
docker stack ps biedronka

# Inspect service configuration
docker service inspect biedronka_prestashop --pretty
```

### Access Container Shell

```powershell
# Get container ID
$containerID = (docker ps -q -f name=biedronka_prestashop | Select-Object -First 1)

# Access shell
docker exec -it $containerID bash
```

### Clear Cache

```powershell
# Clear PrestaShop cache
docker exec $(docker ps -q -f name=biedronka_prestashop | Select-Object -First 1) php bin/console cache:clear
```

---

## Shutdown & Cleanup

### Stop Stack (Preserves Data)

```powershell
# Remove stack (containers stop, volumes persist)
docker stack rm biedronka

# Verify removal
docker stack ls
```

### Full Cleanup (Including Data)

```powershell
# Remove stack
docker stack rm biedronka

# Wait for cleanup (30 seconds)
Start-Sleep -Seconds 30

# Remove volumes (WARNING: deletes database!)
docker volume rm biedronka_mysql_data

# Remove images (optional)
docker rmi biedronka-mysql:latest biedronka-prestashop:latest
```

### Leave Swarm Mode

```powershell
# Leave swarm (WARNING: removes all stacks and services)
docker swarm leave --force
```

---

## Troubleshooting

### Development Mode Issues

**Hot Reload Not Working**

```powershell
# Verify volume mount
docker-compose config | Select-String "themes/biedronka"

# Should show: ../src/themes/biedronka:/var/www/html/themes/biedronka

# Restart compose if needed
docker-compose restart prestashop
```

**Port Already in Use**

```powershell
# Find process using port 8080
netstat -ano | Select-String ":8080"

# Stop compose and free ports
docker-compose down
```

### Production Mode Issues

**Service Won't Start**

```powershell
# Check service errors
docker service ps biedronka_prestashop --no-trunc

# Check detailed logs
docker service logs biedronka_prestashop --tail 100

# Common issue: Images not built
docker images | Select-String "biedronka"
# If missing - rebuild images before deploying stack
```

**Database Connection Errors**

```powershell
# Verify MySQL is running
docker service ls | Select-String "mysql"

# Check MySQL logs for errors
docker service logs biedronka_mysql --tail 50

# Verify network connectivity
docker network inspect biedronka_prestashop_network
```

**Can't Access Website**

1. Verify services are running: `docker service ls`
2. Wait for replicas: `2/2` (not `0/2` or `1/2`)
3. Check logs: `docker service logs biedronka_prestashop`
4. Verify Swarm: `docker node ls` should show `Leader`

**Hot Reload Doesn't Work in Swarm**

This is expected behavior for multi-node Swarm clusters. Our single-node setup preserves hot reload through volume mounts, but in true distributed clusters (multiple servers), hot reload isn't supported. For development with hot reload, use `docker-compose up -d` instead.

---

## Technical Details

### Network Configuration

- **Driver:** overlay (multi-host support)
- **Subnet:** Auto-assigned by Docker
- **Encryption:** Optional (not enabled by default)
- **Attachable:** Yes (allows standalone containers to connect)

### Resource Limits

**MySQL:**

- CPU: 1 core max
- Memory: 1024 MB max
- Replicas: 1 (singleton)

**PrestaShop:**

- CPU: 2 cores max per replica
- Memory: 1024 MB max per replica
- Replicas: 2 (scalable)

### Deployment Strategy

- **Update parallelism:** 1 (one replica at a time)
- **Update delay:** 10 seconds between replicas
- **Update order:** start-first (new container starts before old stops)
- **Rollback:** Automatic on failure

### Health & Restart Policies

- **Restart condition:** on-failure
- **Restart delay:** 5 seconds
- **Max restart attempts:** 3
- **Placement:** MySQL constrained to manager node

---

## Requirements Verification Checklist

### ✅ Cluster Deployment

- [x] Docker Swarm initialized
- [x] Stack deployed with `docker stack deploy`
- [x] Overlay network created
- [x] Multiple service replicas running

### ✅ Shared Database Server

- [x] MySQL deployed as separate service
- [x] PrestaShop replicas connect to shared MySQL instance
- [x] Database accessible via service name (`mysql`)
- [x] Persistent volume for database data

### ✅ Stable Database Connection

- [x] Connection tested via PHP PDO
- [x] All CRUD operations work (products, orders, users)
- [x] No connection drops during normal operation

### ✅ Functional Requirements (Phase I)

- [x] Homepage displays correctly
- [x] Product catalog browsing works
- [x] Add to cart functionality
- [x] Checkout process completes
- [x] User registration/login
- [x] Back Office accessible
- [x] Product management (CRUD)
- [x] Order management
- [x] Customer management

---

## Production Considerations

### Multi-Node Cluster

To add worker nodes to your Swarm cluster:

```bash
# On manager node - get join token
docker swarm join-token worker

# On worker nodes - join cluster
docker swarm join --token SWMTKN-1-xxx <MANAGER_IP>:2377
```

### Security Hardening

1. **Use Docker secrets** for passwords:

   ```powershell
   echo "toor" | docker secret create mysql_root_password -
   ```

2. **Enable overlay network encryption**:

   ```yaml
   networks:
     prestashop_network:
       driver: overlay
       driver_opts:
         encrypted: "true"
   ```

3. **Use reverse proxy** (nginx/Traefik) for SSL termination

### Monitoring

Integrate with:

- **Prometheus** + Grafana for metrics
- **ELK Stack** for log aggregation
- **Portainer** for visual management

---

## Support

For issues or questions:

1. Check logs: `docker service logs <service-name>`
2. Inspect service: `docker service inspect <service-name> --pretty`
3. Review GitHub issues: [biedronka-clone-prestashop](https://github.com/quuixly/biedronka-clone-prestashop)

---

## License

Same as main project - see root LICENSE file.
