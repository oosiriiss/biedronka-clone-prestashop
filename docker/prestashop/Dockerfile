FROM prestashop/prestashop:1.7.8.10


COPY src/themes/classic /var/www/html/themes/classic
COPY src/themes/biedronka /var/www/html/themes/biedronka

RUN chown -R www-data:www-data /var/www/html/themes/biedronka
