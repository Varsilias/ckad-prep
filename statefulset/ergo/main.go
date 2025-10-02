package main

import (
	"context"
	"database/sql"
	"errors"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	_ "github.com/go-sql-driver/mysql"
	"github.com/varsilias/ergo/internal/api"
	"github.com/varsilias/ergo/internal/logging"
	"github.com/varsilias/ergo/internal/middleware"
	"github.com/varsilias/ergo/internal/ui"
)

func main() {
	addr := ":" + getEnv("PORT", "8080")
	logLevel := getEnv("LOG_LEVEL", "info")
	json, _ := strconv.ParseBool(getEnv("LOG_JSON", "false"))
	dsn := getEnv("DSN", "root:root@tcp(localhost:33060)/ergo?charset=utf8mb4&parseTime=True&loc=Local")
	dbType := getEnv("DB_TYPE", "mysql") // mysql|postgres|sqlite

	logger := logging.NewLogger(logLevel, json)

	db, err := sql.Open(dbType, dsn)
	if err != nil {
		logger.Error("db init", "err", err)
		os.Exit(1)
	}

	db.SetConnMaxLifetime(time.Minute * 3)
	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(10)

	mux := chi.NewRouter()
	mux.Handle("/static/*", http.StripPrefix("/static/", http.FileServer(http.Dir("web/static"))))

	modules := registerHandlers(db, logger, mux)

	todoModule := modules[0].(*api.TodoModule) // todo module

	uih, err := ui.New(logger, todoModule.Service())
	if err != nil {
		logger.Error("ui init", "err", err)
		os.Exit(1)
	}

	ui.RegisterRoutes(mux, uih)

	var handler http.Handler = mux
	handler = middleware.Recoverer(logger)(handler)
	handler = middleware.RequestID()(handler)
	handler = middleware.AccessLog(logger)(handler)

	server := http.Server{
		Addr:              addr,
		Handler:           handler,
		ReadTimeout:       15 * time.Second,
		ReadHeaderTimeout: 15 * time.Second,
		WriteTimeout:      60 * time.Second,
		IdleTimeout:       120 * time.Second,
	}

	logger.Info("Lord speak you server is listening", "port", addr)

	// graceful shutdown
	errChan := make(chan error, 1)
	go func() {
		errChan <- server.ListenAndServe()
	}()

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	select {
	case err := <-errChan:
		if errors.Is(err, http.ErrServerClosed) {
			logger.Error("server error", "err", err)
			os.Exit(1)
		}
	case sig := <-sigChan:
		logger.Info("shutdown signal received", "signal", sig.String())
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		logger.Error("graceful shutdown failed", "err", err)
	} else {
		logger.Info("server stopped")
	}

}

func registerHandlers(db *sql.DB, logger *slog.Logger, mux chi.Router) []api.Module {
	modules := []api.Module{
		api.NewTodoModule(db, logger),
		// api.NewUserModule(db, logger),
		// api.NewAuthModule(db, logger),
	}

	// core health route
	mux.Get("/health", api.Health)

	for _, m := range modules {
		m.RegisterRoutes(mux)
	}

	return modules
}

func getEnv(key, def string) string {
	v := os.Getenv(key)
	if v != "" {
		return v
	}
	return def
}
