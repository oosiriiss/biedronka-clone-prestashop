FROM prestashop/prestashop:1.7.8.10


COPY src/classic /var/www/html/themes/classic
COPY src/biedronka /var/www/html/themes/biedronka

RUN chown -R www-data:www-data /var/www/html/themes/biedronka
