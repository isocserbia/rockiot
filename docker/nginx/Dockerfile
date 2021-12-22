FROM nginx:alpine

# Expose HTTP(s) ports
EXPOSE 80/tcp
EXPOSE 443/tcp

# Set ENV variables
ARG BUILD_ARGUMENT_ENV=dev
ENV ENV=$BUILD_ARGUMENT_ENV

# Forward NGINX logs to console
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# Install and update OpenSSL
RUN apk update && \
    apk add --update openssl && \
    rm -rf /var/cache/apk/*

# Copy SSL certs and keys
COPY ./ssl /etc/ssl/

# Copy NGINX configuration
RUN mkdir -p /etc/nginx/sites-enabled
COPY ./config /etc/nginx/

ENTRYPOINT ["nginx", "-g", "daemon off;"]
