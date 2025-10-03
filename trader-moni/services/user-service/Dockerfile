FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
COPY .env ./.env
RUN npm ci
COPY . .
RUN npm run build

FROM gcr.io/distroless/nodejs20-debian11
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=development /app/dist ./dist
COPY --from=development /app/.env ./.env
EXPOSE 3001
CMD ["dist/main.js"]