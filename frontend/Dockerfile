# ── Stage 1: сборка React-приложения ─────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Сначала только зависимости — кешируются если package.json не менялся
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

# Копируем исходники и собираем
COPY . .

# VITE_API_URL будет подставлен через build-arg или .env
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# ── Stage 2: Nginx для раздачи статики ───────────────────────────────────────
FROM nginx:1.25-alpine AS runtime

# Удаляем дефолтный конфиг nginx
RUN rm /etc/nginx/conf.d/default.conf

# Наш конфиг
COPY nginx/nginx.conf /etc/nginx/conf.d/app.conf

# Собранные файлы из builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Непривилегированный пользователь
RUN chown -R nginx:nginx /usr/share/nginx/html \
    && chmod -R 755 /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
