
# Wymuszenie utf8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
# -------------------------------------------------

# Nazwy kontenerow 
$MysqlContainer = "some-mysql"
$PrestaContainer = "prestashop"

# Katalog backupu do przywrocenia
$BackupDir = ".\backup_20260114_211728"

if (-not (Test-Path -Path $BackupDir)) {
    Write-Host "Katalog backupu $BackupDir nie istnieje!" -ForegroundColor Red
    exit 1
}

Write-Host "Przywracanie bazy danych PrestaShop..." -ForegroundColor Cyan

$SqlFileLocal = "$BackupDir/prestashop_db.sql"
$SqlFileRemote = "/tmp/restore_db.sql"

if (Test-Path $SqlFileLocal) {
    Write-Host "Kopiowanie pliku SQL do kontenera..." -ForegroundColor Gray
    docker cp "$SqlFileLocal" "$($MysqlContainer):$SqlFileRemote"
    
    Write-Host "Importowanie SQL wewnatrz kontenera..." -ForegroundColor Gray
    docker exec -i $MysqlContainer bash -c "mysql -u root -ptoor prestashop < $SqlFileRemote"
    
    docker exec -i $MysqlContainer rm $SqlFileRemote
    Write-Host "Baza danych przywrocona." -ForegroundColor Green
} else {
    Write-Host "Nie znaleziono pliku $SqlFileLocal" -ForegroundColor Red
    exit 1
}

# Przywracanie plikow konfiguracyjnych
Write-Host "Przywracanie plikow konfiguracyjnych..." -ForegroundColor Cyan
docker cp "$BackupDir/config/parameters.php" "$($PrestaContainer):/var/www/html/app/config/parameters.php"

if (Test-Path "$BackupDir/config/.htaccess") {
    docker cp "$BackupDir/config/.htaccess" "$($PrestaContainer):/var/www/html/.htaccess"
}

if (Test-Path "$BackupDir/config/robots.txt") {
    docker cp "$BackupDir/config/robots.txt" "$($PrestaContainer):/var/www/html/robots.txt"
}

# Przywracanie motywu
Write-Host "Przywracanie motywu sklepu..." -ForegroundColor Cyan
if (Test-Path "$BackupDir/themes/biedronka") {
    docker cp "$BackupDir/themes/biedronka/." "$($PrestaContainer):/var/www/html/themes/biedronka/"
}

# Przywracanie modulow
Write-Host "Przywracanie modulow..." -ForegroundColor Cyan
if (Test-Path "$BackupDir/modules") {
    docker cp "$BackupDir/modules" "$($PrestaContainer):/var/www/html/"
}

# Przywracanie zdjec produktow, kategorii, bannerow i logo
Write-Host "Przywracanie zdjec i bannerow..." -ForegroundColor Cyan
if (Test-Path "$BackupDir/img") {
    docker cp "$BackupDir/img" "$($PrestaContainer):/var/www/html/"
}

#  Przywracanie tlumaczen
Write-Host "Przywracanie tlumaczen..." -ForegroundColor Cyan
if (Test-Path "$BackupDir/translations") {
    docker cp "$BackupDir/translations" "$($PrestaContainer):/var/www/html/"
}

#  Przywracanie produktow cyfrowych i uploadow
Write-Host "Przywracanie folderow upload i download..." -ForegroundColor Cyan
if (Test-Path "$BackupDir/uploads/upload") {
    docker cp "$BackupDir/uploads/upload" "$($PrestaContainer):/var/www/html/upload"
}
if (Test-Path "$BackupDir/uploads/download") {
    docker cp "$BackupDir/uploads/download" "$($PrestaContainer):/var/www/html/download"
}

#  Przywracanie certyfikatow SSL
if (Test-Path "$BackupDir/certs") {
    Write-Host "Przywracanie certyfikatow SSL..." -ForegroundColor Cyan
    if (-not (Test-Path "./certs")) { New-Item -ItemType Directory -Force -Path "./certs" | Out-Null }
    Copy-Item -Path "$BackupDir/certs/*" -Destination "./certs/" -Recurse -Force
}

# Czyszczenie cache PrestaShop
Write-Host "Czyszczenie cache PrestaShop..." -ForegroundColor Cyan
try {
    docker exec -i $PrestaContainer bash -c "php bin/console cache:clear"
} catch {
    Write-Host "Czyszczenie cache zwrocilo blad" -ForegroundColor Yellow
}


# Bez tego bedzie error o uprawnieniach na windowsie.
Write-Host "Naprawianie uprawnien plikow (to moze chwile potrwac)..." -ForegroundColor Cyan
docker exec -i $PrestaContainer bash -c "chown -R www-data:www-data /var/www/html"

Write-Host "Czyszczenie cache PrestaShop..." -ForegroundColor Cyan
try {
    docker exec -u www-data -i $PrestaContainer bash -c "php bin/console cache:clear"
} catch {
    Write-Host "Ostrzezenie: Pierwsza proba czyszczenia cache nie powiodla sie. Ponawiam..." -ForegroundColor Yellow
}

docker exec -i $PrestaContainer bash -c "chown -R www-data:www-data /var/www/html/var/cache"

Write-Host "Uprawnienia naprawione." -ForegroundColor Green

Write-Host "------------------------------------------------------------" -ForegroundColor Gray
Write-Host "Przywracanie backupu zakonczone. Sklep powinien byc w pelni gotowy." -ForegroundColor Green
