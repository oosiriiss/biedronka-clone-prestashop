#!/usr/bin/env pwsh
# PrestaShop Backup Script
# Creates full backup of shop settings, database, and files

param(
    [Parameter(Mandatory=$false)]
    [string]$BackupName = "shop-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
)

$ErrorActionPreference = "Stop"
$BackupDir = "backups/$BackupName"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  PrestaShop Backup & Export Tool     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan

# Create backup directory structure
Write-Step "Creating backup directory: $BackupDir"
New-Item -ItemType Directory -Force -Path "$BackupDir/database" | Out-Null
New-Item -ItemType Directory -Force -Path "$BackupDir/files" | Out-Null
New-Item -ItemType Directory -Force -Path "$BackupDir/modules" | Out-Null

# Check if containers are running
Write-Step "Checking Docker containers..."
$mysqlContainer = docker ps -q -f "name=mysql" | Select-Object -First 1
$prestashopContainer = docker ps -q -f "name=prestashop" | Select-Object -First 1

if (-not $mysqlContainer) {
    Write-Error "MySQL container not running. Start with: docker-compose up -d"
    exit 1
}

Write-Success "Containers are running"

# Backup database
Write-Step "Exporting full database..."
docker exec $mysqlContainer mysqldump -uroot -ptoor prestashop > "$BackupDir/database/prestashop_full.sql"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to export database - mysqldump failed!"
    exit 1
}

# Verify backup is not empty
$sqlSize = (Get-Item "$BackupDir/database/prestashop_full.sql").Length
if ($sqlSize -lt 10000) {
    Write-Error "Database backup is too small ($sqlSize bytes) - export failed!"
    exit 1
}

$lines = (Get-Content "$BackupDir/database/prestashop_full.sql").Count
Write-Success "Full database exported ($sqlSize bytes, $lines lines)"

Write-Step "Exporting configuration tables..."
docker exec $mysqlContainer mysqldump -uroot -ptoor prestashop ps_configuration > "$BackupDir/database/ps_configuration.sql"
docker exec $mysqlContainer mysqldump -uroot -ptoor prestashop ps_module > "$BackupDir/database/ps_module.sql"
docker exec $mysqlContainer mysqldump -uroot -ptoor prestashop ps_carrier > "$BackupDir/database/ps_carrier.sql"
docker exec $mysqlContainer mysqldump -uroot -ptoor prestashop ps_configuration 2>$null > "$BackupDir/database/ps_configuration.sql"
docker exec $mysqlContainer mysqldump -uroot -ptoor prestashop ps_module 2>$null > "$BackupDir/database/ps_module.sql"
docker exec $mysqlContainer mysqldump -uroot -ptoor prestashop ps_carrier 2>$null > "$BackupDir/database/ps_carrier.sql"
docker exec $mysqlContainer mysqldump -uroot -ptoor prestashop ps_shop 2>$null > "$BackupDir/database/ps_shop.sql"
Write-Success "Configuration tables exported"

# Backup files from PrestaShop container
Write-Step "Copying files from PrestaShop container..."
$prestashopContainer = docker ps -q -f "name=prestashop" | Select-Object -First 1

if (-not $prestashopContainer) {
    Write-Error "PrestaShop container not running. Start with: docker-compose up -d"
    exit 1
}

# Theme Biedronka
Write-Host "  → Biedronka theme..." -NoNewline
docker cp "${prestashopContainer}:/var/www/html/themes/biedronka" "$BackupDir/files/biedronka-theme" 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host " ✓" -ForegroundColor Green } else { Write-Host " ⚠" -ForegroundColor Yellow }

# All themes
Write-Host "  → All themes..." -NoNewline
docker cp "${prestashopContainer}:/var/www/html/themes" "$BackupDir/files/themes" 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host " ✓" -ForegroundColor Green }

# Product images
Write-Host "  → Product images (img/)..." -NoNewline
docker cp "${prestashopContainer}:/var/www/html/img" "$BackupDir/files/img" 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host " ✓" -ForegroundColor Green } else { Write-Host " ⚠" -ForegroundColor Yellow }

# Uploaded files
Write-Host "  → Uploaded files (upload/)..." -NoNewline
docker cp "${prestashopContainer}:/var/www/html/upload" "$BackupDir/files/upload" 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host " ✓" -ForegroundColor Green } else { Write-Host " ⚠" -ForegroundColor Yellow }

# Download files
Write-Host "  → Download files (download/)..." -NoNewline
docker cp "${prestashopContainer}:/var/www/html/download" "$BackupDir/files/download" 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host " ✓" -ForegroundColor Green } else { Write-Host " ⚠" -ForegroundColor Yellow }

# Modules
Write-Host "  → Modules..." -NoNewline
docker cp "${prestashopContainer}:/var/www/html/modules" "$BackupDir/files/modules" 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host " ✓" -ForegroundColor Green }

# Config files
Write-Host "  → Configuration files..." -NoNewline
docker cp "${prestashopContainer}:/var/www/html/config" "$BackupDir/files/config" 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host " ✓" -ForegroundColor Green }

# Backup SSL from host
Write-Step "Copying SSL certificates from host..."
if (Test-Path "docker/certs") {
    Copy-Item -Recurse -Force "docker/certs" "$BackupDir/files/certs"
    Write-Success "SSL certificates copied"
} else {
    Write-Host "⚠ No SSL certs on host" -ForegroundColor Yellow
}

Write-Success "Container files backed up"

# List enabled modules
Write-Step "Exporting enabled modules list..."
docker exec $mysqlContainer mysql -uroot -ptoor prestashop -e "SELECT name, active FROM ps_module WHERE active=1" 2>$null > "$BackupDir/modules/enabled_modules.txt"
Write-Success "Modules list exported"

# Create backup info file
Write-Step "Creating backup metadata..."
$backupInfo = @"
PrestaShop Backup Information
=============================

Backup Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Backup Name: $BackupName
PrestaShop Version: 1.7.8.10
PHP Version: 7.4
MySQL Version: 5.7/8.0

Description:
This backup contains complete PrestaShop shop settings and configuration.
It enables full restoration in case of failure.

Included Data:
- Full database dump (prestashop_full.sql)
- Shop configuration (ps_configuration.sql)
- Modules configuration (ps_module.sql, ps_carrier.sql)
- All themes (themes/)
- Biedronka theme (biedronka-theme/)
- Product images (img/)
- Uploaded files (upload/)
- Download files (download/)
- Modules files (modules/)
- Configuration files (config/)
- SSL certificates (certs/)
- Enabled modules list

Restore Instructions:
1. Use restore-settings.ps1 script
2. Or manually import SQL files and copy theme files
3. See docs/BACKUP_RESTORE.md for details

Created by: export-settings.ps1
"@

$backupInfo | Out-File -FilePath "$BackupDir/backup-info.txt" -Encoding UTF8

Write-Success "Backup metadata created"

# Summary
Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         Backup Completed! ✅          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`nBackup Location: " -NoNewline
Write-Host "$BackupDir" -ForegroundColor Cyan

Write-Host "`nBackup Contents:" -ForegroundColor Yellow
Get-ChildItem -Recurse $BackupDir | Select-Object FullName | Format-Table -AutoSize

Write-Host "`nTo restore this backup, run:" -ForegroundColor Yellow
Write-Host "  .\scripts\restore-settings.ps1 -BackupPath `"$BackupDir`"" -ForegroundColor Cyan

Write-Host "`n✨ Done!`n" -ForegroundColor Green
