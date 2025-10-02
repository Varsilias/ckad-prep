package storage

import (
	"context"
	"database/sql"
	"fmt"
	"log/slog"
	"strconv"

	"github.com/varsilias/ergo/internal/repository"
	"github.com/varsilias/ergo/pkg/domain"
)

type MysqlTodoRepo struct {
	db  *sql.DB
	log *slog.Logger
}

func NewMysqlTodoRepo(db *sql.DB, log *slog.Logger) repository.TodoRepository {
	return &MysqlTodoRepo{db: db, log: log}
}

func (r *MysqlTodoRepo) Find(ctx context.Context, args domain.ListTodoParam) ([]domain.Todo, error) {
	query := `
		SELECT id, title, completed
		FROM todos
		ORDER BY id
		LIMIT ? OFFSET ?
	`

	rows, err := r.db.QueryContext(ctx, query, args.PerPage, (args.Page-1)*args.PerPage)
	if err != nil {
		r.log.Error("mysql repo", "model", "todo", "err", err.Error())
		return nil, err
	}
	defer rows.Close()
	items := []domain.Todo{}
	for rows.Next() {
		var i domain.Todo
		if err := rows.Scan(
			&i.ID,
			&i.Title,
			&i.Completed,
		); err != nil {
			return nil, err
		}
		items = append(items, i)
	}

	if err := rows.Close(); err != nil {
		return nil, err
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return items, nil
}

func (r *MysqlTodoRepo) FindByID(ctx context.Context, ID int64) (domain.Todo, error) {
	query := `
		SELECT id, title, completed
		FROM todos
		WHERE id = ?
	`

	row := r.db.QueryRowContext(ctx, query, ID)

	var i domain.Todo
	err := row.Scan(
		&i.ID,
		&i.Title,
		&i.Completed,
	)
	return i, err
}

func (r *MysqlTodoRepo) Save(ctx context.Context, todo string) (*domain.Todo, error) {
	query := `
		INSERT INTO todos
		(title)
		VALUES (?)
	`

	res, err := r.db.ExecContext(ctx, query, todo)
	if err != nil {
		return nil, err
	}

	id, err := res.LastInsertId()
	if err != nil {
		return nil, err
	}

	newTodo, err := r.FindByID(ctx, id)

	if err != nil {
		return nil, err
	}

	return &newTodo, nil
}

func (r *MysqlTodoRepo) Update(ctx context.Context, args domain.UpdateTodoParam) (*domain.Todo, error) {
	query := `
		UPDATE todos
		SET  completed = ?
		WHERE id = ?
	`
	r.log.Debug("db prepare", "update", "args", "ID", strconv.Itoa(args.ID), "completed", strconv.FormatBool(args.Completed))

	res, err := r.db.ExecContext(ctx, query, args.Completed, args.ID)
	if err != nil {
		r.log.Debug("db query", "action", "update", "res", res)
		return nil, err
	}

	rowsAffected, err := res.RowsAffected()
	if err != nil {
		r.log.Debug("db query", "action", "update", "res", res)
		return nil, err
	}

	if rowsAffected == 0 {
		r.log.Debug("db query", "action", "update", "res", res)
	}

	newTodo, err := r.FindByID(ctx, int64(args.ID))

	if err != nil {
		r.log.Debug("db query", "action", "update", "res", res)
		return nil, err
	}

	return &newTodo, err
}

func (r *MysqlTodoRepo) Delete(ctx context.Context, ID int64) error {
	query := `
		DELETE FROM todos
		WHERE id = ?
	`

	res, err := r.db.ExecContext(ctx, query, ID)
	if err != nil {
		return err
	}

	rowsAffected, err := res.RowsAffected()
	if err != nil {
		return err
	}

	if rowsAffected == 0 {
		return fmt.Errorf("no todo found with id %d", ID)
	}

	return nil
}
