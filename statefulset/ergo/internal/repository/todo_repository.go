package repository

import (
	"context"

	"github.com/varsilias/ergo/pkg/domain"
)

type TodoRepository interface {
	Save(ctx context.Context, todo string) (*domain.Todo, error)
	Update(ctx context.Context, param domain.UpdateTodoParam) (*domain.Todo, error)
	Find(ctx context.Context, param domain.ListTodoParam) ([]domain.Todo, error)
	FindByID(ctx context.Context, ID int64) (domain.Todo, error)
	Delete(ctx context.Context, ID int64) error
}
