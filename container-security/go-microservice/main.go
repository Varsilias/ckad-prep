package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/gorilla/mux"
	"github.com/varsilias/k8s/details"
)

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/", rootHandler)
	r.HandleFunc("/health", healthHandler)
	r.HandleFunc("/details", detailsHandler)
	log.Println("Server has started!!")
	log.Fatal(http.ListenAndServe(":80", r))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("Checking application health")
	response := map[string]string{
		"status":    "Ok",
		"timestamp": time.Now().String(),
	}
	json.NewEncoder(w).Encode(response)
}

func rootHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("Serving the homepage")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "Application is up and running")
}

func detailsHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Fetching the details")
	hostname, err := details.GetHostname()
	if err != nil {
		panic(err)
	}
	IP, _ := details.GetIP()
	fmt.Println(hostname, IP)

	response := map[string]string{
		"hostname": hostname,
		"ip":       IP,
	}
	json.NewEncoder(w).Encode(response)
}
