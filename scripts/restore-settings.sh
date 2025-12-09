#!/bin/bash
# PrestaShop Restore Script for Linux/macOS

BACKUP_PATH="$1"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "\n${CYAN}==> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

if [ -z "$BACKUP_PATH" ]; then
    echo "Usage: $0 <backup-path>"
    echo "Example: $0 backups/shop-backup-20251209-183045"
    exit 1
fi

echo -e "\n${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  PrestaShop Restore Tool              ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"

# Verify backup
if [ ! -d "$BACKUP_PATH" ]; then
    print_error "Backup not found: $BACKUP_PATH"
fi

print_step "Backup found: $BACKUP_PATH"

# Check containers
MYSQL_CONTAINER=$(docker ps -q -f "name=mysql" | head -1)
if [ -z "$MYSQL_CONTAINER" ]; then
    print_error "MySQL container not running. Start with: docker-compose up -d"
fi

# Warning
echo -e "\n${YELLOW}⚠️  WARNING: This will replace current shop data!${NC}"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Restore database
print_step "Restoring full database..."
if [ -f "$BACKUP_PATH/database/prestashop_full.sql" ]; then
    docker exec -i $MYSQL_CONTAINER mysql -uroot -ptoor prestashop < "$BACKUP_PATH/database/prestashop_full.sql"
    print_success "Database restored"
else
    print_error "Database backup not found at $BACKUP_PATH/database/prestashop_full.sql"
fi

# Restore files to container
print_step "Restoring files to PrestaShop container..."
PRESTASHOP_CONTAINER=$(docker ps -q -f "name=prestashop" | head -1)

if [ -z "$PRESTASHOP_CONTAINER" ]; then
    print_error "PrestaShop container not running. Start with: cd docker && docker-compose up -d"
fi

# Restore themes
if [ -d "$BACKUP_PATH/files/themes" ]; then
    echo "  → Restoring all themes..."
    docker exec $PRESTASHOP_CONTAINER rm -rf /var/www/html/themes 2>/dev/null
    docker cp "$BACKUP_PATH/files/themes" $PRESTASHOP_CONTAINER:/var/www/html/
    echo -e "    ${GREEN}✓${NC} Themes restored"
fi

# Restore Biedronka theme (fallback)
if [ -d "$BACKUP_PATH/files/biedronka-theme" ]; then
    echo "  → Restoring Biedronka theme..."
    docker exec $PRESTASHOP_CONTAINER mkdir -p /var/www/html/themes 2>/dev/null
    docker cp "$BACKUP_PATH/files/biedronka-theme" $PRESTASHOP_CONTAINER:/var/www/html/themes/biedronka
    echo -e "    ${GREEN}✓${NC} Biedronka theme restored"
fi

# Restore images
if [ -d "$BACKUP_PATH/files/img" ]; then
    echo "  → Restoring product images..."
    docker exec $PRESTASHOP_CONTAINER rm -rf /var/www/html/img 2>/dev/null
    docker cp "$BACKUP_PATH/files/img" $PRESTASHOP_CONTAINER:/var/www/html/
    echo -e "    ${GREEN}✓${NC} Images restored"
fi

# Restore uploads
if [ -d "$BACKUP_PATH/files/upload" ]; then
    echo "  → Restoring uploaded files..."
    docker exec $PRESTASHOP_CONTAINER rm -rf /var/www/html/upload 2>/dev/null
    docker cp "$BACKUP_PATH/files/upload" $PRESTASHOP_CONTAINER:/var/www/html/
    echo -e "    ${GREEN}✓${NC} Uploads restored"
fi

# Restore downloads
if [ -d "$BACKUP_PATH/files/download" ]; then
    echo "  → Restoring download files..."
    docker exec $PRESTASHOP_CONTAINER rm -rf /var/www/html/download 2>/dev/null
    docker cp "$BACKUP_PATH/files/download" $PRESTASHOP_CONTAINER:/var/www/html/
    echo -e "    ${GREEN}✓${NC} Downloads restored"
fi

# Restore modules
if [ -d "$BACKUP_PATH/files/modules" ]; then
    echo "  → Restoring modules..."
    docker exec $PRESTASHOP_CONTAINER rm -rf /var/www/html/modules 2>/dev/null
    docker cp "$BACKUP_PATH/files/modules" $PRESTASHOP_CONTAINER:/var/www/html/
    echo -e "    ${GREEN}✓${NC} Modules restored"
fi

# Restore config
if [ -d "$BACKUP_PATH/files/config" ]; then
    echo "  → Restoring configuration files..."
    docker cp "$BACKUP_PATH/files/config" $PRESTASHOP_CONTAINER:/var/www/html/
    echo -e "    ${GREEN}✓${NC} Config restored"
fi

print_success "Files restored to container"

# Restore SSL to host
print_step "Restoring SSL certificates to host..."
if [ -d "$BACKUP_PATH/files/certs" ]; then
    rm -rf docker/certs
    cp -r "$BACKUP_PATH/files/certs" docker/certs
    print_success "SSL certificates restored"
fi

# Fix permissions in container
print_step "Fixing file permissions..."
docker exec $PRESTASHOP_CONTAINER chown -R www-data:www-data /var/www/html/themes /var/www/html/img /var/www/html/upload /var/www/html/download /var/www/html/modules /var/www/html/config 2>/dev/null
print_success "Permissions fixed"

# Clear cache
print_step "Clearing cache..."
PRESTASHOP_CONTAINER=$(docker ps -q -f "name=prestashop" | head -1)
if [ -n "$PRESTASHOP_CONTAINER" ]; then
    docker exec $PRESTASHOP_CONTAINER rm -rf /var/www/html/var/cache/* 2>/dev/null
    print_success "Cache cleared"
fi

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       Restore Completed! ✅           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}Shop accessible at:${NC}"
echo -e "  ${CYAN}Frontend: http://localhost:8080${NC}"
echo -e "  ${CYAN}Admin: http://localhost:8080/admin-dev${NC}\n"
