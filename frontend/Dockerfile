# Use the official Apache image
FROM httpd:alpine

# Copy HTML, CSS, JS files to the Apache document root
COPY . /usr/local/apache2/htdocs/

# Expose port 80 (default HTTP port)
EXPOSE 80

# Start Apache
CMD ["httpd", "-D", "FOREGROUND"]
