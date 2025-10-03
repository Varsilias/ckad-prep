package main

import (
	"encoding/json"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"time"
)

type Config struct {
	Port                   string
	UserServiceURL         string
	OrderServiceURL        string
	PaymentServiceURL      string
	NotificationServiceURL string
}

type HealthResponse struct {
	Status    string    `json:"status"`
	Timestamp time.Time `json:"timestamp"`
	Service   string    `json:"service"`
	Version   string    `json:"version"`
}

func loadConfig() Config {
	return Config{
		Port:                   getEnv("PORT", "8080"),
		UserServiceURL:         getEnv("USER_SERVICE_URL", "http://localhost:3001"),
		OrderServiceURL:        getEnv("ORDER_SERVICE_URL", "http://localhost:8081"),
		PaymentServiceURL:      getEnv("PAYMENT_SERVICE_URL", "http://localhost:8082"),
		NotificationServiceURL: getEnv("NOTIFICATION_SERVICE_URL", "http://localhost:3002"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	response := HealthResponse{
		Status:    "healthy",
		Timestamp: time.Now(),
		Service:   "gateway-service",
		Version:   getEnv("SERVICE_VERSION", "1.0.0"),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func createProxy(targetURL string) http.Handler {
	url, _ := url.Parse(targetURL)
	return httputil.NewSingleHostReverseProxy(url)
}

func main() {
	config := loadConfig()

	// Create proxies
	userProxy := createProxy(config.UserServiceURL)
	orderProxy := createProxy(config.OrderServiceURL)
	paymentProxy := createProxy(config.PaymentServiceURL)
	notificationProxy := createProxy(config.NotificationServiceURL)

	// Routes
	http.HandleFunc("/health", healthHandler)
	http.Handle("/users/", http.StripPrefix("/users", userProxy))
	http.Handle("/orders/", http.StripPrefix("/orders", orderProxy))
	http.Handle("/payments/", http.StripPrefix("/payments", paymentProxy))
	http.Handle("/notifications/", http.StripPrefix("/notifications", notificationProxy))

	log.Printf("Gateway service starting on port %s", config.Port)
	log.Fatal(http.ListenAndServe(":"+config.Port, nil))
}
