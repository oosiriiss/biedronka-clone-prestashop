#!/bin/bash
# PrestaShop Backup Script for Linux/macOS

BACKUP_NAME="${1:-shop-backup-$(date +%Y%m%d-%H%M%S)}"
BACKUP_DIR="backups/$BACKUP_NAME"

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

echo -e "\n${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  PrestaShop Backup & Export Tool     ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"

# Create directories
print_step "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR/database"
mkdir -p "$BACKUP_DIR/files"
mkdir -p "$BACKUP_DIR/modules"

# Check containers
print_step "Checking Docker containers..."
MYSQL_CONTAINER=$(docker ps -q -f "name=mysql" | head -1)

if [ -z "$MYSQL_CONTAINER" ]; then
    print_error "MySQL container not running. Start with: docker-compose up -d"
fi

print_success "Containers are running"

# Backup database
print_step "Exporting full database..."
docker exec $MYSQL_CONTAINER mysqldump -uroot -ptoor prestashop 2>/dev/null > "$BACKUP_DIR/database/prestashop_full.sql"
print_success "Full database exported"

print_step "Exporting configuration tables..."
docker exec $MYSQL_CONTAINER mysqldump -uroot -ptoor prestashop ps_configuration 2>/dev/null > "$BACKUP_DIR/database/ps_configuration.sql"
docker exec $MYSQL_CONTAINER mysqldump -uroot -ptoor prestashop ps_module 2>/dev/null > "$BACKUP_DIR/database/ps_module.sql"
docker exec $MYSQL_CONTAINER mysqldump -uroot -ptoor prestashop ps_carrier 2>/dev/null > "$BACKUP_DIR/database/ps_carrier.sql"
print_success "Configuration tables exported"

# Backup files from PrestaShop container
print_step "Copying files from PrestaShop container..."
PRESTASHOP_CONTAINER=$(docker ps -q -f "name=prestashop" | head -1)

if [ -z "$PRESTASHOP_CONTAINER" ]; then
    print_error "PrestaShop container not running. Start with: cd docker && docker-compose up -d"
fi

# Theme Biedronka
echo "  → Biedronka theme..."
docker cp $PRESTASHOP_CONTAINER:/var/www/html/themes/biedronka "$BACKUP_DIR/files/biedronka-theme" 2>/dev/null && \
    echo -e "    ${GREEN}✓${NC} Copied" || \
    echo -e "    ${YELLOW}⚠${NC} Not found"

# All themes (backup)
echo "  → All themes..."
docker cp $PRESTASHOP_CONTAINER:/var/www/html/themes "$BACKUP_DIR/files/themes" 2>/dev/null && \
    echo -e "    ${GREEN}✓${NC} Copied"

# Product images
echo "  → Product images (img/)..."
docker cp $PRESTASHOP_CONTAINER:/var/www/html/img "$BACKUP_DIR/files/img" 2>/dev/null && \
    echo -e "    ${GREEN}✓${NC} Copied" || \
    echo -e "    ${YELLOW}⚠${NC} No images"

# Uploaded files
echo "  → Uploaded files (upload/)..."
docker cp $PRESTASHOP_CONTAINER:/var/www/html/upload "$BACKUP_DIR/files/upload" 2>/dev/null && \
    echo -e "    ${GREEN}✓${NC} Copied" || \
    echo -e "    ${YELLOW}⚠${NC} No uploads"

# Download files (invoices, PDFs)
echo "  → Download files (download/)..."
docker cp $PRESTASHOP_CONTAINER:/var/www/html/download "$BACKUP_DIR/files/download" 2>/dev/null && \
    echo -e "    ${GREEN}✓${NC} Copied" || \
    echo -e "    ${YELLOW}⚠${NC} No downloads"

# Modules (custom/modified only)
echo "  → Modules..."
docker cp $PRESTASHOP_CONTAINER:/var/www/html/modules "$BACKUP_DIR/files/modules" 2>/dev/null && \
    echo -e "    ${GREEN}✓${NC} Copied"

# Config files
echo "  → Configuration files..."
docker cp $PRESTASHOP_CONTAINER:/var/www/html/config "$BACKUP_DIR/files/config" 2>/dev/null && \
    echo -e "    ${GREEN}✓${NC} Copied"

# Backup SSL from host
print_step "Copying SSL certificates from host..."
if [ -d "docker/certs" ]; then
    cp -r docker/certs "$BACKUP_DIR/files/certs"
    print_success "SSL certificates copied"
else
    echo -e "${YELLOW}⚠${NC} No SSL certs on host"
fi

print_success "Container files backed up"

# Modules list
print_step "Exporting enabled modules list..."
docker exec $MYSQL_CONTAINER mysql -uroot -ptoor prestashop -e "SELECT name, active FROM ps_module WHERE active=1" 2>/dev/null > "$BACKUP_DIR/modules/enabled_modules.txt"
print_success "Modules list exported"

# Create backup info
cat > "$BACKUP_DIR/backup-info.txt" << EOF
PrestaShop Backup Information
=============================

Backup Date: $(date '+%Y-%m-%d %H:%M:%S')
Backup Name: $BACKUP_NAME
PrestaShop Version: 1.7.8.10
PHP Version: 7.4
MySQL Version: 5.7/8.0

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
1. Use restore-settings.sh script
2. Or manually: 
   - Import SQL: mysql < database/prestashop_full.sql
   - Copy files back to container
3. See docs/BACKUP_RESTORE.md for details
EOF

print_success "Backup metadata created"

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Backup Completed! ✅          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}Backup Location:${NC} ${CYAN}$BACKUP_DIR${NC}"
echo -e "\n${YELLOW}To restore:${NC} ${CYAN}./scripts/restore-settings.sh $BACKUP_DIR${NC}\n"
