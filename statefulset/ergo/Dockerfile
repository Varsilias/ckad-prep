# ── ASSETS ─────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS assets
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund
COPY web/static ./web/static
COPY web/templates ./web/templates

# Build tailwind -> web/static/dist/app.css
RUN npm run tw:prod


# ── GO BUILD ───────────────────────────────────────────────────────────────────
FROM golang:1.24.7-alpine AS builder
WORKDIR /app

# Install git for 'go mod' and allow private modules
RUN apk update && \
    apk add --no-cache git ca-certificates

COPY go.mod go.sum ./
RUN go mod download

# Copy the whole source (except what's ignored by .dockerignore)
COPY . .
# Bring in built assets from the Node stage
COPY --from=assets /app/web/static/dist ./web/static/dist

RUN go build -o /out/app .

# ── RUNTIME ────────────────────────────────────────────────────────────────────
FROM gcr.io/distroless/static:nonroot
WORKDIR /app
COPY --from=builder /out/app /app/app
# templates + assets must be present at runtime (UI reads from disk)
COPY --from=builder /app/web /app/web
EXPOSE 8080
USER nonroot:nonroot
ENV ADDR=8080 LOG_LEVEL=info LOG_JSON=false
ENTRYPOINT ["/app/app"]