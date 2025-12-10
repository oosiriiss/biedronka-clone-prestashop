#!/bin/bash

# Simple PrestaShop Backup Script
# Based on standard backup approach

# Main settings
DOMAIN_DIR="../src/themes/biedronka"
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="backup-${DATE}"

# MySQL Settings (Docker)
MYSQL_CONTAINER=$(docker ps -q -f "name=mysql" | head -1)
DB_USER="root"
DB_PASS="toor"
DB_NAME="prestashop"

# Create backup directory
[ ! -d "$BACKUP_DIR" ] && mkdir -p $BACKUP_DIR
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

echo "Starting backup: ${BACKUP_NAME}"

# MySQL Backup
echo "Backing up database..."
docker exec $MYSQL_CONTAINER mysqldump -u$DB_USER -p$DB_PASS --opt --databases $DB_NAME | gzip -9 > "${BACKUP_DIR}/${BACKUP_NAME}/database.sql.gz"

# Files Backup (Biedronka theme)
echo "Backing up Biedronka theme..."
tar czf "${BACKUP_DIR}/${BACKUP_NAME}/biedronka-theme.tar.gz" -C ../src/themes biedronka

# Backup container files
echo "Backing up container files..."
PRESTASHOP_CONTAINER=$(docker ps -q -f "name=prestashop" | head -1)

# Images
docker cp $PRESTASHOP_CONTAINER:/var/www/html/img "${BACKUP_DIR}/${BACKUP_NAME}/img-temp"
tar czf "${BACKUP_DIR}/${BACKUP_NAME}/img.tar.gz" -C "${BACKUP_DIR}/${BACKUP_NAME}" img-temp
rm -rf "${BACKUP_DIR}/${BACKUP_NAME}/img-temp"

# Modules
docker cp $PRESTASHOP_CONTAINER:/var/www/html/modules "${BACKUP_DIR}/${BACKUP_NAME}/modules-temp"
tar czf "${BACKUP_DIR}/${BACKUP_NAME}/modules.tar.gz" -C "${BACKUP_DIR}/${BACKUP_NAME}" modules-temp
rm -rf "${BACKUP_DIR}/${BACKUP_NAME}/modules-temp"

echo "✅ Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}"
echo ""
echo "Backup contains:"
ls -lh "${BACKUP_DIR}/${BACKUP_NAME}"
