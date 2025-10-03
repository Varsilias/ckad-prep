# Makefile
.PHONY: build up down test clean logs

# Build all services
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Test all health endpoints
test:
	@echo "Testing Gateway Service..."
	curl -s http://localhost:8080/health | jq .
	@echo "Testing User Service..."
	curl -s http://localhost:3001/health | jq .
	@echo "Testing Order Service..."
	curl -s http://localhost:8081/health | jq .
	@echo "Testing Payment Service..."
	curl -s http://localhost:8082/health | jq .
	@echo "Testing Notification Service..."
	curl -s http://localhost:3002/health | jq .

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Build individual services
build-gateway:
	docker build -t trader-moni/gateway-service ./services/gateway-service

build-user:
	docker build -t trader-moni/user-service ./services/user-service

build-order:
	docker build -t trader-moni/order-service ./services/order-service

build-payment:
	docker build -t trader-moni/payment-service ./services/payment-service

build-notification:
	docker build -t trader-moni/notification-service ./services/notification-service