// main.go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gorilla/mux"
)

type Order struct {
	ID        string    `json:"id"`
	UserID    string    `json:"userId"`
	Amount    float64   `json:"amount"`
	Status    string    `json:"status"`
	CreatedAt time.Time `json:"createdAt"`
}

type Config struct {
	Port           string
	PaymentService string
	DatabaseURL    string
}

var orders []Order

func loadConfig() Config {
	return Config{
		Port:           getEnv("PORT", "8081"),
		PaymentService: getEnv("PAYMENT_SERVICE_URL", "http://localhost:8082"),
		DatabaseURL:    getEnv("DATABASE_URL", "memory://localhost"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	response := map[string]interface{}{
		"status":    "healthy",
		"timestamp": time.Now(),
		"service":   "order-service",
		"version":   getEnv("SERVICE_VERSION", "1.0.0"),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func createOrderHandler(w http.ResponseWriter, r *http.Request) {
	var order Order
	if err := json.NewDecoder(r.Body).Decode(&order); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	order.ID = fmt.Sprintf("order-%d", time.Now().Unix())
	order.Status = "pending"
	order.CreatedAt = time.Now()

	orders = append(orders, order)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(order)
}

func getOrdersHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(orders)
}

func main() {
	config := loadConfig()

	r := mux.NewRouter()
	r.HandleFunc("/health", healthHandler)
	r.HandleFunc("/orders", createOrderHandler).Methods("POST")
	r.HandleFunc("/orders", getOrdersHandler).Methods("GET")

	log.Printf("Order service starting on port %s", config.Port)
	log.Fatal(http.ListenAndServe(":"+config.Port, r))
}
