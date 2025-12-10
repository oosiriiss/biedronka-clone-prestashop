#!/bin/bash

# Simple PrestaShop Restore Script
# Based on standard restore approach

BACKUP_PATH="$1"

if [ -z "$BACKUP_PATH" ]; then
    echo "Usage: $0 <backup-folder>"
    echo "Example: $0 backups/backup-20251210-153000"
    exit 1
fi

if [ ! -d "$BACKUP_PATH" ]; then
    echo "Error: Backup not found: $BACKUP_PATH"
    exit 1
fi

echo "╔════════════════════════════════════════╗"
echo "║  PrestaShop Simple Restore Tool       ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Restoring from: $BACKUP_PATH"
echo ""

# MySQL Settings
MYSQL_CONTAINER=$(docker ps -q -f "name=mysql" | head -1)
PRESTASHOP_CONTAINER=$(docker ps -q -f "name=prestashop" | head -1)
DB_USER="root"
DB_PASS="toor"
DB_NAME="prestashop"

if [ -z "$MYSQL_CONTAINER" ]; then
    echo "Error: MySQL container not running"
    exit 1
fi

# Restore database
# echo "→ Restoring database..."
# if [ -f "$BACKUP_PATH/database.sql.gz" ]; then
#     gunzip < "$BACKUP_PATH/database.sql.gz" | docker exec -i $MYSQL_CONTAINER mysql -u$DB_USER -p$DB_PASS $DB_NAME
#     echo "  ✓ Database restored"
# else
#     echo "  ✗ Database backup not found"
# fi

echo "→ Restoring database..."
if [ -f "$BACKUP_PATH/database.sql.gz" ]; then
    # ✅ 1. DROP and CREATE database FIRST
    echo "  → Recreating database..."
    docker exec $MYSQL_CONTAINER mysql -u$DB_USER -p$DB_PASS -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME;" 2>/dev/null
    
    # ✅ 2. THEN import SQL
    echo "  → Importing SQL (10-20 seconds)..."
    gunzip < "$BACKUP_PATH/database.sql.gz" | docker exec -i $MYSQL_CONTAINER mysql -u$DB_USER -p$DB_PASS $DB_NAME 2>/dev/null
    
    # ✅ 3. Verify import worked
    TABLE_COUNT=$(docker exec $MYSQL_CONTAINER mysql -u$DB_USER -p$DB_PASS $DB_NAME -e "SHOW TABLES;" 2>/dev/null | wc -l)
    if [ $TABLE_COUNT -gt 10 ]; then
        echo "  ✓ Database restored ($TABLE_COUNT tables)"
    else
        echo "  ✗ FAILED - only $TABLE_COUNT tables restored!"
        exit 1
    fi
else
    echo "  ✗ Database backup not found"
    exit 1
fi

# Restore Biedronka theme
echo "→ Restoring Biedronka theme..."
if [ -f "$BACKUP_PATH/biedronka-theme.tar.gz" ]; then
    rm -rf ../src/themes/biedronka
    tar xzf "$BACKUP_PATH/biedronka-theme.tar.gz" -C ../src/themes
    echo "  ✓ Theme restored"
else
    echo "  ✗ Theme backup not found"
fi

# Restore images
echo "→ Restoring images..."
if [ -f "$BACKUP_PATH/img.tar.gz" ]; then
    tar xzf "$BACKUP_PATH/img.tar.gz" -C /tmp
    docker cp /tmp/img-temp/. $PRESTASHOP_CONTAINER:/var/www/html/img/
    rm -rf /tmp/img-temp
    echo "  ✓ Images restored"
else
    echo "  ✗ Images backup not found"
fi

# Restore modules
echo "→ Restoring modules..."
if [ -f "$BACKUP_PATH/modules.tar.gz" ]; then
    tar xzf "$BACKUP_PATH/modules.tar.gz" -C /tmp
    docker cp /tmp/modules-temp/. $PRESTASHOP_CONTAINER:/var/www/html/modules/
    rm -rf /tmp/modules-temp
    
    # Remove problematic modules
    docker exec $PRESTASHOP_CONTAINER rm -rf /var/www/html/modules/ps_checkout
    docker exec $PRESTASHOP_CONTAINER rm -rf /var/www/html/modules/ps_mbo
    echo "  ✓ Modules restored (ps_checkout removed)"
else
    echo "  ✗ Modules backup not found"
fi

# Fix permissions
echo "→ Fixing permissions..."
docker exec $PRESTASHOP_CONTAINER chown -R www-data:www-data /var/www/html/themes /var/www/html/img /var/www/html/modules

# Clear cache
echo "→ Clearing cache..."
docker exec $PRESTASHOP_CONTAINER rm -rf /var/www/html/var/cache/*

echo ""
echo "╔════════════════════════════════════════╗"
echo "║       Restore Completed! ✅            ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Shop: http://localhost:8080"
