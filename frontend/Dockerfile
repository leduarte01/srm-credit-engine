# syntax=docker/dockerfile:1.7

# ---------- Builder ----------
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies first to leverage the layer cache.
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# Build the SPA. VITE_API_BASE_URL is configurable at build time so the
# bundle can target different backends (in docker-compose we keep it as a
# same-origin /api path so nginx can reverse-proxy to the backend).
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY . .
RUN npm run build


# ---------- Runtime ----------
FROM nginx:1.27-alpine AS runtime

# Drop the default site config and ship our SPA + reverse proxy config.
RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=5 \
  CMD wget -qO- http://localhost/healthz >/dev/null 2>&1 || exit 1

CMD ["nginx", "-g", "daemon off;"]
