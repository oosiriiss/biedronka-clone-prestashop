FROM prestashop/prestashop:1.7.8.10

# Enable SSL and configure Apache
RUN a2enmod ssl headers rewrite

COPY src/themes/classic /var/www/html/themes/classic
COPY src/themes/biedronka /var/www/html/themes/biedronka
COPY docker/prestashop/ssl.conf /etc/apache2/sites-available/ssl.conf

RUN chown -R www-data:www-data /var/www/html/themes/biedronka \
  && a2ensite ssl.conf

EXPOSE 80 443
