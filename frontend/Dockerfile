# Use an official Nginx image as the base
FROM nginx:alpine

# Copy the static content (HTML, CSS, JavaScript) to the Nginx server
COPY ./html /usr/share/nginx/html
COPY ./css /usr/share/nginx/html/css
COPY ./js /usr/share/nginx/html/js

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (Nginx default)
EXPOSE 80