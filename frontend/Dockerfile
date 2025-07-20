FROM nginx:alpine

# Удаляем дефолтный конфиг
RUN rm /etc/nginx/conf.d/default.conf

# Установка envsubst
RUN apk add --no-cache gettext && \
    rm -rf /var/cache/apk/*

# Копируем наш конфиг
COPY nginx/templates/default.conf /etc/nginx/conf.d/

# Копируем статику
COPY public/ /usr/share/nginx/html/

# Права
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

CMD ["sh", "-c", "nginx -t && nginx -g 'daemon off;'"]