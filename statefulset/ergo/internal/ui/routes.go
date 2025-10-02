package ui

import (
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/go-chi/chi/v5"
	"github.com/varsilias/ergo/pkg/domain"
)

func RegisterRoutes(mux *chi.Mux, h *UI) {
	mux.Get("/", h.Home)
	mux.Post("/ui/todo", h.TodoPost)
	mux.Patch("/ui/todo/{id}", h.TodoPatch)
	mux.Delete("/ui/todo/{id}", h.TodoDelete)
}

func (u *UI) Home(w http.ResponseWriter, r *http.Request) {
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
	todos, err := u.todoController.List(r.Context(), domain.ListTodoParam{Page: int64(page), PerPage: int64(limit)})
	if err != nil {
		http.Error(w, "an error occured", http.StatusInternalServerError)
		return
	}

	hostname := os.Getenv("HOSTNAME")
	if hostname == "" {
		hostname = "default"
	}
	u.render(w, "home.html", map[string]any{"Todos": todos, "Hostname": hostname}, http.StatusOK)
}

func (u *UI) TodoPost(w http.ResponseWriter, r *http.Request) {
	_ = r.ParseForm()
	u.log.Info("ui contr", "todo", "post", "title", r.Form.Get("todo_title"))
	title := strings.TrimSpace(r.Form.Get("todo_title"))

	if title == "" {
		http.Error(w, "enter a todo title", 400)
		return
	}

	todo, err := u.todoController.Create(r.Context(), title)
	if err != nil {
		http.Error(w, "an error occured", http.StatusInternalServerError)
		return
	}
	u.render(w, "todo.html", todo, http.StatusOK, Headers{"HX-Trigger": "todoAdded"})
}

func (u *UI) TodoPatch(w http.ResponseWriter, r *http.Request) {
	_ = r.ParseForm()
	completedStr := strings.TrimSpace(r.Form.Get("completed"))

	completed, err := strconv.ParseBool(completedStr)
	if err != nil {
		u.log.Info("ui contr", "todo", "patch", "error", err.Error())
		http.Error(w, "invalid request body", 400)
		return
	}

	idParam := chi.URLParam(r, "id")
	id, err := strconv.Atoi(idParam)
	if err != nil {
		u.log.Info("ui contr", "todo", "patch", "error", err.Error())
		http.Error(w, "invalid request", 400)
		return
	}

	u.log.Info("ui contr", "todo", "patch", "completed", completedStr, "ID", idParam)

	todo, err := u.todoController.Update(r.Context(), domain.UpdateTodoParam{ID: id, Completed: completed})
	if err != nil {
		u.log.Info("ui contr query", "todo", "patch", "error", err.Error())
		http.Error(w, "an error occured", http.StatusInternalServerError)
		return
	}
	u.render(w, "todo.html", todo, http.StatusOK)
}

func (u *UI) TodoDelete(w http.ResponseWriter, r *http.Request) {

	idParam := chi.URLParam(r, "id")
	id, err := strconv.Atoi(idParam)
	if err != nil {
		u.log.Info("ui contr", "todo", "patch", "error", err.Error())
		http.Error(w, "invalid request", 400)
		return
	}

	u.log.Info("ui contr", "todo", "patch", "ID", idParam)

	err = u.todoController.Delete(r.Context(), int64(id))
	if err != nil {
		u.log.Info("ui contr query", "todo", "patch", "error", err.Error())
		http.Error(w, "an error occured", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusOK)
}
