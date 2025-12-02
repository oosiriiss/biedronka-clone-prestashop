# biedronka-clone-prestashop

Academic project developed for a university course. The goal is to create an e-commerce website inspired by the Biedronka supermarket, implemented using the PrestaShop platform. The project demonstrates skills in CMS configuration, template customization, and online store management.

# Team members

- Kamil
- Bartek
- Kuba

# Software version

- **Project version:** 1.0.0
- **Technologies / Requirements:**
  - PHP: 7.4
  - PrestaShop: 1.7.8.10
  - MySQL: 5.7

# Google Analitics is on projekty.pg0@gmail.com

# Installation & Deployment

This project supports **two deployment modes** using the same `docker-compose.yml` configuration:

1. **Development Mode (docker-compose)** - Hot reload, fast startup, easy debugging
2. **Production Mode (docker stack)** - Cluster deployment, load balancing, meets project requirements

---

## Development Mode (Recommended for Daily Work)

Use `docker-compose.yml` (in `docker/` directory) for daily development with hot reload and fast iteration.

### Quick Start

```powershell
# Start environment (from docker/ directory)
cd docker
docker-compose up -d

# View logs
docker-compose logs -f prestashop

# Stop environment
docker-compose down
```

### Development Workflow

1. **Edit theme files** in `src/themes/biedronka/`
2. **Refresh browser** - changes apply immediately ✅
3. **Clear cache** if needed:
   ```powershell
   cd docker
   docker-compose exec prestashop php bin/console cache:clear
   ```

**Access:**

- **Frontend:** http://localhost:8080 or https://localhost
- **Admin panel:** http://localhost:8080/admin-dev
  - Email: `makajler@szpont.pl`
  - Password: `password`

**Theme selection:** Design → Theme & Logo → Biedronka → "Use this theme"

---

## Production Mode (Cluster Deployment for Presentation)

Use `docker-compose-prod.yml` with `docker stack deploy` to meet cluster requirements: shared database, load balancing, multiple replicas.

### Prerequisites

- Docker Engine 20.10+ with Swarm support
- PowerShell (Windows) or Bash (Linux/macOS)
- Minimum 4GB RAM available

### Quick Start

**Windows PowerShell (automated):**

```powershell
# One-command deployment
.\scripts\deploy-swarm.ps1 -Action deploy
```

**Linux/macOS Bash (automated):**

```bash
# Make script executable
chmod +x scripts/deploy-swarm.sh

# One-command deployment
./scripts/deploy-swarm.sh deploy
```

<!-- ./scripts/deploy-swarm.sh deploy          # Deploy całego stacka
./scripts/deploy-swarm.sh scale 3         # Skaluj do 3 replik
./scripts/deploy-swarm.sh update          # Update po zmianach w kodzie
./scripts/deploy-swarm.sh status          # Status stacka
./scripts/deploy-swarm.sh stop            # Stop (zachowuje dane)
./scripts/deploy-swarm.sh cleanup         # Usuń wszystko -->

**Manual deployment:**

```powershell
# 1. Initialize Swarm cluster
docker swarm init

# 2. Build images
cd docker
docker build -t biedronka-mysql:latest -f mysql/Dockerfile ..
docker build -t biedronka-prestashop:latest -f prestashop/Dockerfile ..

# 3. Deploy stack
docker stack deploy -c docker-compose-prod.yml biedronka

# 4. Check status
docker stack services biedronka
# Wait until: biedronka_prestashop 2/2 replicas
```

**Access:** Same URLs as development mode (http://localhost:8080 or https://localhost)

📖 **Full documentation:** See [docs/SWARM_DEPLOYMENT.md](docs/SWARM_DEPLOYMENT.md)

### Swarm Management

**Windows PowerShell:**

```powershell
# Scale PrestaShop replicas
.\scripts\deploy-swarm.ps1 -Action scale -Replicas 3

# Update stack (after code changes)
.\scripts\deploy-swarm.ps1 -Action update

# Check status
.\scripts\deploy-swarm.ps1 -Action status

# Stop stack (preserves data)
.\scripts\deploy-swarm.ps1 -Action stop

# Full cleanup (removes everything)
.\scripts\deploy-swarm.ps1 -Action cleanup
```

**Linux/macOS Bash:**

```bash
# Scale PrestaShop replicas
./scripts/deploy-swarm.sh scale 3

# Update stack (after code changes)
./scripts/deploy-swarm.sh update

# Check status
./scripts/deploy-swarm.sh status

# Stop stack (preserves data)
./scripts/deploy-swarm.sh stop

# Full cleanup (removes everything)
./scripts/deploy-swarm.sh cleanup
```

---

## Switching Between Modes

### From Development to Production

```powershell
cd docker
docker-compose down
docker swarm init  # if not already done
.\..\scripts\deploy-swarm.ps1 -Action deploy
```

### From Production to Development

```powershell
docker stack rm biedronka
# Wait 30 seconds for cleanup
cd docker
docker-compose up -d
```

---

## Legacy Installation (Not Recommended)

### Linux/macOS:

```bash
cd scripts/
chmod +x ./install.sh
sudo ./install.sh
```

### Run:

```bash
cd scripts/
chmod +x ./run.sh
sudo ./run.sh
```

# License

This project is licensed under the **MIT License**.

# Additional info

Frontend: http://localhost:8080/
Admin panel: http://localhost:8080/admin-dev
