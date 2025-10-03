# Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /app
# COPY go.mod go.sum ./
COPY go.mod ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o gateway-service

# Runtime stage
FROM gcr.io/distroless/static-debian11
COPY --from=builder /app/gateway-service /
EXPOSE 8080
CMD ["/gateway-service"]