package service

import (
	"context"

	"github.com/varsilias/ergo/internal/repository"
	"github.com/varsilias/ergo/pkg/domain"
)

type TodoController interface {
	List(ctx context.Context, param domain.ListTodoParam) ([]domain.Todo, error)
	Get(ctx context.Context, ID int64) (*domain.Todo, error)
	Create(ctx context.Context, title string) (*domain.Todo, error)
	Update(ctx context.Context, param domain.UpdateTodoParam) (*domain.Todo, error)
	Delete(ctx context.Context, ID int64) error
}

type TodoService struct {
	repo repository.TodoRepository
}

func NewTodoService(repo repository.TodoRepository) *TodoService {
	return &TodoService{repo: repo}
}

func (s *TodoService) List(ctx context.Context, param domain.ListTodoParam) ([]domain.Todo, error) {
	todos, err := s.repo.Find(ctx, param)
	if err != nil {
		return nil, err
	}

	return todos, nil
}

func (s *TodoService) Get(ctx context.Context, ID int64) (*domain.Todo, error) {
	todo, err := s.repo.FindByID(ctx, ID)
	if err != nil {
		return nil, err
	}

	return &todo, nil
}

func (s *TodoService) Create(ctx context.Context, title string) (*domain.Todo, error) {
	return s.repo.Save(ctx, title)
}

func (s *TodoService) Update(ctx context.Context, param domain.UpdateTodoParam) (*domain.Todo, error) {
	return s.repo.Update(ctx, param)
}

func (s *TodoService) Delete(ctx context.Context, ID int64) error {
	return s.repo.Delete(ctx, ID)
}
