package api

import (
	"database/sql"
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"
	"strconv"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/varsilias/ergo/internal/service"
	"github.com/varsilias/ergo/internal/storage"
	"github.com/varsilias/ergo/pkg/domain"
	"github.com/varsilias/ergo/pkg/utils"
)

type TodoHandler struct {
	log *slog.Logger
	svc *service.TodoService
}

func NewTodoHandler(log *slog.Logger, svc *service.TodoService) *TodoHandler {
	return &TodoHandler{
		log: log,
		svc: svc,
	}
}

type TodoModule struct {
	handler *TodoHandler
	service service.TodoController
}

func NewTodoModule(db *sql.DB, log *slog.Logger) *TodoModule {
	repo := storage.NewMysqlTodoRepo(db, log)
	svc := service.NewTodoService(repo)
	return &TodoModule{
		handler: NewTodoHandler(log, svc),
		service: svc,
	}
}

func (m *TodoModule) Service() service.TodoController {
	return m.service
}

func (m *TodoModule) RegisterRoutes(r chi.Router) {
	r.Mount("/api", r.Group(func(r chi.Router) {
		r.Get("/todos", m.handler.ListTodos)
		r.Post("/todos", m.handler.CreateTodo)
		r.Get("/todos/{id}", m.handler.GetTodo)
		r.Patch("/todos/{id}", m.handler.UpdateTodo)
		r.Delete("/todos/{id}", m.handler.DeleteTodo)
	}))
}

func (h *TodoHandler) ListTodos(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		utils.JSON(w, http.StatusMethodNotAllowed, map[string]any{
			"status":    false,
			"message":   "Method not allowed",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	queryParams := r.URL.Query()
	pageStr := queryParams.Get("name")
	limitStr := queryParams.Get("limit")

	page, err := strconv.Atoi(pageStr)
	if err != nil || page < 1 {
		page = 1
	}

	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit < 1 {
		limit = 10
	}

	todos, err := h.svc.List(r.Context(), domain.ListTodoParam{Page: int64(page), PerPage: int64(limit)})
	if err != nil {
		h.log.Error("handler", "module", "todo", "err", err)
		utils.JSON(w, http.StatusInternalServerError, map[string]any{
			"status":    false,
			"message":   "an error occured when fetching todo list",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	utils.JSON(w, http.StatusOK, map[string]any{
		"status":  true,
		"message": "todos fetched succesfully",
		"data":    todos,
		"meta": domain.ListTodoParam{
			Page:    int64(page),
			PerPage: int64(limit),
		},
	})
}

func (h *TodoHandler) GetTodo(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		utils.JSON(w, http.StatusMethodNotAllowed, map[string]any{
			"status":    false,
			"message":   "Method not allowed",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}
	idParam := chi.URLParam(r, "id")

	id, err := strconv.Atoi(idParam)
	if err != nil || id < 1 {
		utils.JSON(w, http.StatusBadRequest, map[string]any{
			"status":    false,
			"message":   "invalid url param",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	todo, err := h.svc.Get(r.Context(), int64(id))

	if err != nil {
		h.log.Error("handler", "module", "todo", "err", err)
		if errors.Is(err, sql.ErrNoRows) {
			utils.JSON(w, http.StatusNotFound, map[string]any{
				"status":    false,
				"message":   "todo not found",
				"timestamp": time.Now().UTC().Format(time.RFC3339),
			})
			return
		}
		utils.JSON(w, http.StatusInternalServerError, map[string]any{
			"status":    false,
			"message":   "an error occured when fetching todo",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	utils.JSON(w, http.StatusOK, map[string]any{
		"status":  true,
		"message": "todo fetched succesfully",
		"data":    todo,
	})
}

func (h *TodoHandler) CreateTodo(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		utils.JSON(w, http.StatusMethodNotAllowed, map[string]any{
			"status":    false,
			"message":   "Method not allowed",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	var req struct {
		Title string `json:"title"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		utils.JSON(w, http.StatusBadRequest, map[string]any{
			"status":    false,
			"message":   "invalid request body",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	if req.Title == "" {
		utils.JSON(w, http.StatusBadRequest, map[string]any{
			"status":    false,
			"message":   "title cannot be empty",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	todo, err := h.svc.Create(r.Context(), req.Title)

	if err != nil {
		h.log.Error("handler", "module", "todo", "err", err)
		utils.JSON(w, http.StatusInternalServerError, map[string]any{
			"status":    false,
			"message":   "an error occured when creating todo",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	utils.JSON(w, http.StatusOK, map[string]any{
		"status":  true,
		"message": "todo created succesfully",
		"data":    todo,
	})
}

func (h *TodoHandler) UpdateTodo(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPatch {
		utils.JSON(w, http.StatusMethodNotAllowed, map[string]any{
			"status":    false,
			"message":   "Method not allowed",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	idParam := chi.URLParam(r, "id")

	id, err := strconv.Atoi(idParam)
	if err != nil || id < 1 {
		utils.JSON(w, http.StatusBadRequest, map[string]any{
			"status":    false,
			"message":   "invalid url param",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	var req struct {
		Completed bool `json:"completed"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		utils.JSON(w, http.StatusBadRequest, map[string]any{
			"status":    false,
			"message":   "invalid request body",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	todo, err := h.svc.Update(r.Context(), domain.UpdateTodoParam{
		ID:        id,
		Completed: req.Completed,
	})

	if err != nil {
		h.log.Error("handler", "module", "todo", "err", err)
		utils.JSON(w, http.StatusInternalServerError, map[string]any{
			"status":    false,
			"message":   "an error occured when updating todo",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	utils.JSON(w, http.StatusOK, map[string]any{
		"status":  true,
		"message": "todo updated succesfully",
		"data":    todo,
	})
}

func (h *TodoHandler) DeleteTodo(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodDelete {
		utils.JSON(w, http.StatusMethodNotAllowed, map[string]any{
			"status":    false,
			"message":   "Method not allowed",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}
	idParam := chi.URLParam(r, "id")

	id, err := strconv.Atoi(idParam)
	if err != nil || id < 1 {
		utils.JSON(w, http.StatusBadRequest, map[string]any{
			"status":    false,
			"message":   "invalid url param",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	err = h.svc.Delete(r.Context(), int64(id))

	if err != nil {
		h.log.Error("handler", "module", "todo", "err", err)
		if errors.Is(err, sql.ErrNoRows) {
			utils.JSON(w, http.StatusNotFound, map[string]any{
				"status":    false,
				"message":   "todo not found",
				"timestamp": time.Now().UTC().Format(time.RFC3339),
			})
			return
		}
		utils.JSON(w, http.StatusInternalServerError, map[string]any{
			"status":    false,
			"message":   "an error occured when deleting todo",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
		return
	}

	utils.JSON(w, http.StatusOK, map[string]any{
		"status":  true,
		"message": "todo deleted succesfully",
		"data":    nil,
	})
}
