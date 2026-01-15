FROM prestashop/prestashop:1.7.8.10

# Enable Apache modules
RUN a2enmod ssl headers rewrite

# Copy themes
COPY src/themes/classic /var/www/html/themes/classic
COPY src/themes/biedronka /var/www/html/themes/biedronka

# Copy SSL vhost
COPY docker/prestashop/ssl.conf /etc/apache2/sites-available/ssl.conf

# Copy HTTP redirect vhost
COPY docker/prestashop/000-default.conf /etc/apache2/sites-available/000-default.conf

# Enable sites
RUN a2ensite ssl.conf \
 && a2ensite 000-default.conf

# Permissions
RUN chown -R www-data:www-data /var/www/html/themes/biedronka

EXPOSE 80 443
