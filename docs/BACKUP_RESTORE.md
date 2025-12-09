<!-- docker exec -it some-mysql mysql -uroot -ptoor prestashop -e "DROP TABLE ps_configuration;" -->
# Backup & Restore Guide

Complete guide for backing up and restoring PrestaShop shop settings.

---

## Quick Start

### Create Backup

**Windows:**

```powershell
.\scripts\export-settings.ps1
```

**Linux/macOS:**

```bash
chmod +x scripts/export-settings.sh
./scripts/export-settings.sh
```

### Restore Backup

**Windows:**

```powershell
.\scripts\restore-settings.ps1 -BackupPath "backups\shop-backup-20251209-183045"
```

**Linux/macOS:**

```bash
./scripts/restore-settings.sh backups/shop-backup-20251209-183045
```

---

## What is Backed Up

### Database Tables:

- `prestashop_full.sql` - Complete database dump
- `ps_configuration.sql` - Shop configuration (domain, SSL, modules settings)
- `ps_module.sql` - Installed modules
- `ps_carrier.sql` - Shipping carriers
- `ps_shop.sql` - Multi-shop settings

### Files:

- `biedronka-theme/` - Custom theme files
- `certs/` - SSL certificates
- `enabled_modules.txt` - List of active modules

### Metadata:

- `backup-info.txt` - Backup timestamp, versions, description

---

## Backup Structure

```
backups/shop-backup-20251209-183045/
├── database/
│   ├── prestashop_full.sql
│   ├── ps_configuration.sql
│   ├── ps_module.sql
│   ├── ps_carrier.sql
│   └── ps_shop.sql
├── files/
│   ├── biedronka-theme/
│   └── certs/
├── modules/
│   └── enabled_modules.txt
└── backup-info.txt
```

---

## Usage Examples

### 1. Regular Backup (Before Updates)

```powershell
# Before updating PrestaShop or modules
.\scripts\export-settings.ps1

# Backup created: backups/shop-backup-20251209-120000/
```

### 2. Named Backup

```powershell
# Create backup with custom name
.\scripts\export-settings.ps1 -BackupName "before-theme-update"

# Result: backups/before-theme-update/
```

### 3. Restore After Failure

```powershell
# 1. List available backups
ls backups/

# 2. Restore specific backup
.\scripts\restore-settings.ps1 -BackupPath "backups\shop-backup-20251209-120000"

# 3. Verify shop works
# http://localhost:8080
```

---

## Automated Backups

### Daily Backup (Scheduled Task - Windows)

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\path\to\scripts\export-settings.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "PrestaShop Daily Backup"
```

### Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/project && ./scripts/export-settings.sh
```

---

## Disaster Recovery Scenarios

### Scenario 1: Database Corruption

```powershell
# 1. Stop shop
cd docker
docker-compose down

# 2. Restore from backup
.\scripts\restore-settings.ps1 -BackupPath "backups\latest-backup"

# 3. Start shop
docker-compose up -d
```

### Scenario 2: Accidental Module Deletion

```powershell
# Restore only database (keeps current files)
$mysqlContainer = docker ps -q -f "name=mysql" | Select-Object -First 1
Get-Content "backups\shop-backup-20251209\database\ps_module.sql" | docker exec -i $mysqlContainer mysql -uroot -ptoor prestashop
```

### Scenario 3: Theme Corruption

```powershell
# Restore only theme files
Copy-Item -Recurse -Force "backups\shop-backup-20251209\files\biedronka-theme" "src\themes\biedronka"
```

---

## Best Practices

### 1. Backup Schedule

- **Daily:** Automated backups at 2 AM
- **Before updates:** Manual backup before any changes
- **After major changes:** Backup after adding products/categories

### 2. Retention Policy

- Keep last 7 daily backups
- Keep monthly backups for 6 months
- Archive yearly backups permanently

### 3. Storage

- Store backups in Git repository (`backups/`)
- Additional copy on external storage (Google Drive, Dropbox)
- Critical backups on separate server

### 4. Verification

```powershell
# Test restore monthly
.\scripts\restore-settings.ps1 -BackupPath "backups\test-backup"
# Verify shop works: http://localhost:8080
```

---

## Troubleshooting

### Error: "MySQL container not running"

**Solution:**

```powershell
cd docker
docker-compose up -d
# Wait 30 seconds for MySQL to start
.\scripts\export-settings.ps1
```

### Error: "Access denied for user root"

**Solution:**

```powershell
# Check MySQL password in docker-compose.yml
# Default: root / toor
docker exec -it $(docker ps -q -f name=mysql) mysql -uroot -ptoor
```

### Backup file too large

**Solution:**

```powershell
# Compress backup
Compress-Archive -Path "backups\shop-backup-20251209" -DestinationPath "backups\shop-backup-20251209.zip"

# Upload compressed file to cloud storage
```

### Restore takes too long

**Solution:**

```powershell
# Restore only essential tables
$mysqlContainer = docker ps -q -f "name=mysql" | Select-Object -First 1

# Configuration only
Get-Content "backups\backup\database\ps_configuration.sql" | docker exec -i $mysqlContainer mysql -uroot -ptoor prestashop

# Skip large product tables if not needed
```

---

## Manual Backup (Alternative)

### Export Database Only

```powershell
docker exec $(docker ps -q -f name=mysql) mysqldump -uroot -ptoor prestashop > manual-backup.sql
```

### Import Database Only

```powershell
Get-Content manual-backup.sql | docker exec -i $(docker ps -q -f name=mysql) mysql -uroot -ptoor prestashop
```

---

## Backup Validation

### Verify Backup Integrity

```powershell
# Check SQL file size
Get-Item "backups\shop-backup-20251209\database\prestashop_full.sql" | Select-Object Length

# Test SQL import (dry run)
Get-Content "backups\backup\database\prestashop_full.sql" | Select-Object -First 10

# Verify theme files exist
Test-Path "backups\backup\files\biedronka-theme"
```

---

## Requirements Met ✅

- ✅ **Export shop settings** - All configuration tables exported
- ✅ **Saved in Git repository** - Stored in `backups/` directory
- ✅ **Enable restoration** - Full restore scripts provided
- ✅ **Disaster recovery** - Complete database + files backup
- ✅ **Documentation** - This guide + inline comments

---

## Support

For issues or questions:

1. Check [Installation.md](Installation.md) for Docker setup
2. Check [SWARM_DEPLOYMENT.md](SWARM_DEPLOYMENT.md) for production deployment
3. Review backup logs in terminal output
4. Verify containers running: `docker ps`
