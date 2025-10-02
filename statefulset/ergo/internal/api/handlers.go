package api

import (
	"net/http"
	"os"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/varsilias/ergo/pkg/utils"
)

type Module interface {
	RegisterRoutes(r chi.Router)
}

// Health is a basic liveness endpoint.
func Health(w http.ResponseWriter, r *http.Request) {
	res := map[string]any{
		"status":    true,
		"message":   "ergo the migo",
		"timestamp": time.Now().UTC().Format(time.RFC3339),
		"hostname":  os.Getenv("HOSTNAME"),
		"pod_ip":    os.Getenv("POD_IP"),
	}
	utils.JSON(w, http.StatusOK, res)
}
