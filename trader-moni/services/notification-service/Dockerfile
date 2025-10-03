FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY server.js .
EXPOSE 3002
USER node
CMD ["node", "server.js"]