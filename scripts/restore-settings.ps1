#!/usr/bin/env pwsh
# PrestaShop Restore Script
# Restores shop settings from backup

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupPath
)

$ErrorActionPreference = "Stop"

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
Write-Host "║  PrestaShop Restore Tool              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan

# Verify backup exists
if (-not (Test-Path $BackupPath)) {
    Write-Error "Backup not found: $BackupPath"
    exit 1
}

Write-Step "Backup found: $BackupPath"

# Check containers
Write-Step "Checking Docker containers..."
$mysqlContainer = docker ps -q -f "name=mysql" | Select-Object -First 1

if (-not $mysqlContainer) {
    Write-Error "MySQL container not running. Start with: docker-compose up -d"
    exit 1
}

# Warning
Write-Host "`n⚠️  WARNING: This will replace current shop data!" -ForegroundColor Yellow
$confirm = Read-Host "Continue? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "Restore cancelled"
    exit 0
}

# Restore database
Write-Step "Restoring full database..."
if (Test-Path "$BackupPath/database/prestashop_full.sql") {
    Get-Content "$BackupPath/database/prestashop_full.sql" | docker exec -i $mysqlContainer mysql -uroot -ptoor prestashop
    Write-Success "Database restored"
} else {
    Write-Error "Database backup not found at $BackupPath/database/prestashop_full.sql"
    exit 1
}

# Restore files to container
Write-Step "Restoring files to PrestaShop container..."
$prestashopContainer = docker ps -q -f "name=prestashop" | Select-Object -First 1

if (-not $prestashopContainer) {
    Write-Error "PrestaShop container not running. Start with: docker-compose up -d"
    exit 1
}

# Restore themes
if (Test-Path "$BackupPath/files/themes") {
    Write-Host "  → Restoring all themes..." -NoNewline
    docker exec $prestashopContainer rm -rf /var/www/html/themes 2>$null
    docker cp "$BackupPath/files/themes" "${prestashopContainer}:/var/www/html/"
    Write-Host " ✓" -ForegroundColor Green
}

# Restore Biedronka theme (fallback)
if (Test-Path "$BackupPath/files/biedronka-theme") {
    Write-Host "  → Restoring Biedronka theme..." -NoNewline
    docker exec $prestashopContainer mkdir -p /var/www/html/themes 2>$null
    docker cp "$BackupPath/files/biedronka-theme" "${prestashopContainer}:/var/www/html/themes/biedronka"
    Write-Host " ✓" -ForegroundColor Green
}

# Restore images
if (Test-Path "$BackupPath/files/img") {
    Write-Host "  → Restoring product images..." -NoNewline
    docker exec $prestashopContainer rm -rf /var/www/html/img 2>$null
    docker cp "$BackupPath/files/img" "${prestashopContainer}:/var/www/html/"
    Write-Host " ✓" -ForegroundColor Green
}

# Restore uploads
if (Test-Path "$BackupPath/files/upload") {
    Write-Host "  → Restoring uploaded files..." -NoNewline
    docker exec $prestashopContainer rm -rf /var/www/html/upload 2>$null
    docker cp "$BackupPath/files/upload" "${prestashopContainer}:/var/www/html/"
    Write-Host " ✓" -ForegroundColor Green
}

# Restore downloads
if (Test-Path "$BackupPath/files/download") {
    Write-Host "  → Restoring download files..." -NoNewline
    docker exec $prestashopContainer rm -rf /var/www/html/download 2>$null
    docker cp "$BackupPath/files/download" "${prestashopContainer}:/var/www/html/"
    Write-Host " ✓" -ForegroundColor Green
}

# Restore modules
if (Test-Path "$BackupPath/files/modules") {
    Write-Host "  → Restoring modules..." -NoNewline
    docker exec $prestashopContainer rm -rf /var/www/html/modules 2>$null
    docker cp "$BackupPath/files/modules" "${prestashopContainer}:/var/www/html/"
    Write-Host " ✓" -ForegroundColor Green
}

# Restore config
if (Test-Path "$BackupPath/files/config") {
    Write-Host "  → Restoring configuration files..." -NoNewline
    docker cp "$BackupPath/files/config" "${prestashopContainer}:/var/www/html/"
    Write-Host " ✓" -ForegroundColor Green
}

Write-Success "Files restored to container"

# Restore SSL to host
Write-Step "Restoring SSL certificates to host..."
if (Test-Path "$BackupPath/files/certs") {
    Remove-Item -Recurse -Force "docker/certs" -ErrorAction SilentlyContinue
    Copy-Item -Recurse -Force "$BackupPath/files/certs" "docker/certs"
    Write-Success "SSL certificates restored"
}

# Fix permissions in container
Write-Step "Fixing file permissions..."
docker exec $prestashopContainer chown -R www-data:www-data /var/www/html/themes /var/www/html/img /var/www/html/upload /var/www/html/download /var/www/html/modules /var/www/html/config 2>$null
Write-Success "Permissions fixed"

# Clear cache
Write-Step "Clearing PrestaShop cache..."
$prestashopContainer = docker ps -q -f "name=prestashop" | Select-Object -First 1
if ($prestashopContainer) {
    docker exec $prestashopContainer rm -rf /var/www/html/var/cache/* 2>$null
    Write-Success "Cache cleared"
}

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║       Restore Completed! ✅           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`nShop should be accessible at:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:8080" -ForegroundColor Cyan
Write-Host "  Admin: http://localhost:8080/admin-dev" -ForegroundColor Cyan

Write-Host "`n✨ Done!`n" -ForegroundColor Green
