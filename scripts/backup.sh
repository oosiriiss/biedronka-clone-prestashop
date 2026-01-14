#!/bin/bash
# backup-prestashop.sh
# Skrypt do pełnego backupu PrestaShop 1.7 w Docker Compose

# Nazwy kontenerów z docker-compose.yml
MYSQL_CONTAINER="some-mysql"
PRESTA_CONTAINER="prestashop"

# Katalog backupu na hoście
BACKUP_DIR="./backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Tworzenie katalogu backupu: $BACKUP_DIR"

# 1️⃣ Eksport bazy danych
echo "Eksport bazy danych PrestaShop..."
docker exec -i $MYSQL_CONTAINER mysqldump -u root -ptoor prestashop > "$BACKUP_DIR/prestashop_db.sql"
echo "Baza danych wyeksportowana do $BACKUP_DIR/prestashop_db.sql"

# 2️⃣ Kopiowanie konfiguracji sklepu
echo "Kopiowanie plików konfiguracyjnych..."
mkdir -p "$BACKUP_DIR/config"
docker cp $PRESTA_CONTAINER:/var/www/html/app/config/parameters.php "$BACKUP_DIR/config/parameters.php"

# 3️⃣ Kopiowanie motywu
echo "Kopiowanie motywu sklepu..."
mkdir -p "$BACKUP_DIR/themes"
docker cp $PRESTA_CONTAINER:/var/www/html/themes/biedronka "$BACKUP_DIR/themes/"

# 4️⃣ Kopiowanie modułów
echo "Kopiowanie modułów..."
mkdir -p "$BACKUP_DIR/modules"
docker cp $PRESTA_CONTAINER:/var/www/html/modules "$BACKUP_DIR/"

# 5️⃣ Kopiowanie zdjęć produktów, kategorii, bannerów i logo
echo "Kopiowanie zdjęć i bannerów..."
mkdir -p "$BACKUP_DIR/img"
docker cp $PRESTA_CONTAINER:/var/www/html/img "$BACKUP_DIR/"

echo "Pełny backup PrestaShop zapisany w katalogu: $BACKUP_DIR"

echo "Backup zakończony. Możesz teraz dodać katalog do repozytorium Git."
