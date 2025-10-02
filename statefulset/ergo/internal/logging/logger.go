package logging

import (
	"log/slog"
	"os"
	"strings"
)

var Logger *slog.Logger

func NewLogger(logLevel string, json bool) *slog.Logger {
	level := parseLevel(logLevel)
	opts := &slog.HandlerOptions{AddSource: true, Level: level}
	var handler slog.Handler

	if json {
		handler = slog.NewJSONHandler(os.Stdout, opts)
	} else {
		handler = slog.NewTextHandler(os.Stdout, opts)
	}

	return slog.New(handler)

}

func parseLevel(s string) slog.Level {
	s = strings.ToLower(s)
	switch s {
	case "warn":
		return slog.LevelWarn
	case "debug":
		return slog.LevelDebug
	case "error":
		return slog.LevelError
	default:
		return slog.LevelInfo
	}
}
