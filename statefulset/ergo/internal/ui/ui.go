package ui

import (
	"html/template"
	"log/slog"
	"net/http"

	"github.com/varsilias/ergo/internal/service"
)

type UI struct {
	log            *slog.Logger
	tpl            *template.Template
	todoController service.TodoController
}

func New(log *slog.Logger, todoController service.TodoController) (*UI, error) {
	t := template.New("root")
	var err error

	if t, err = t.ParseGlob("web/templates/*.html"); err != nil {
		return nil, err
	}
	if t, err = t.ParseGlob("web/templates/partials/*.html"); err != nil {
		return nil, err
	}
	return &UI{
		tpl:            t,
		log:            log,
		todoController: todoController,
	}, nil
}

type Headers map[string]string

func (u *UI) render(w http.ResponseWriter, name string, data any, status int, headers ...Headers) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	for _, h := range headers {
		for k, v := range h {
			w.Header().Set(k, v)
		}
	}
	w.WriteHeader(status)
	if err := u.tpl.ExecuteTemplate(w, name, data); err != nil {
		u.errTpl(w, err)
	}
}

func (u *UI) errTpl(w http.ResponseWriter, err error) {
	u.log.Error("template execute", "err", err)
	_, _ = w.Write([]byte("<pre>template error: " + err.Error() + "</pre>"))
}
