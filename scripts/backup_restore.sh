#!/bin/bash
# full-restore-prestashop.sh
# Pełne przywracanie backupu PrestaShop w Docker Compose

# Nazwy kontenerów z docker-compose.yml
MYSQL_CONTAINER="some-mysql"
PRESTA_CONTAINER="prestashop"

# Katalog backupu do przywrócenia
BACKUP_DIR="./backup_to_restore"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Katalog backupu $BACKUP_DIR nie istnieje!"
    exit 1
fi

# 1️⃣ Przywracanie bazy danych
echo "Przywracanie bazy danych PrestaShop..."
docker exec -i $MYSQL_CONTAINER mysql -u root -ptoor prestashop < "$BACKUP_DIR/prestashop_db.sql"
echo "Baza danych przywrócona."

# 2️⃣ Przywracanie plików konfiguracyjnych
echo "Przywracanie plików konfiguracyjnych..."
docker cp "$BACKUP_DIR/config/parameters.php" $PRESTA_CONTAINER:/var/www/html/app/config/parameters.php
if [ -f "$BACKUP_DIR/config/.htaccess" ]; then
    docker cp "$BACKUP_DIR/config/.htaccess" $PRESTA_CONTAINER:/var/www/html/.htaccess
fi
if [ -f "$BACKUP_DIR/config/robots.txt" ]; then
    docker cp "$BACKUP_DIR/config/robots.txt" $PRESTA_CONTAINER:/var/www/html/robots.txt
fi

# 3️⃣ Przywracanie motywu
echo "Przywracanie motywu sklepu..."
docker cp "$BACKUP_DIR/themes/biedronka" $PRESTA_CONTAINER:/var/www/html/themes/biedronka

# 4️⃣ Przywracanie modułów
echo "Przywracanie modułów..."
docker cp "$BACKUP_DIR/modules" $PRESTA_CONTAINER:/var/www/html/

# 5️⃣ Przywracanie zdjęć produktów, kategorii, bannerów i logo
echo "Przywracanie zdjęć i bannerów..."
docker cp "$BACKUP_DIR/img" $PRESTA_CONTAINER:/var/www/html/

# 6️⃣ Przywracanie tłumaczeń
echo "Przywracanie tłumaczeń..."
docker cp "$BACKUP_DIR/translations" $PRESTA_CONTAINER:/var/www/html/

# 7️⃣ Przywracanie produktów cyfrowych i uploadów
echo "Przywracanie folderów upload i download..."
docker cp "$BACKUP_DIR/uploads/upload" $PRESTA_CONTAINER:/var/www/html/upload
docker cp "$BACKUP_DIR/uploads/download" $PRESTA_CONTAINER:/var/www/html/download

# 8️⃣ Przywracanie certyfikatów SSL
if [ -d "$BACKUP_DIR/certs" ]; then
    echo "Przywracanie certyfikatów SSL..."
    cp -r "$BACKUP_DIR/certs/" ./certs/
fi

# 9️⃣ Czyszczenie cache PrestaShop
echo "Czyszczenie cache PrestaShop..."
docker exec -it $PRESTA_CONTAINER bash -c "php bin/console cache:clear"

echo "Przywracanie backupu zakończone. Sklep powinien być w pełni gotowy."
