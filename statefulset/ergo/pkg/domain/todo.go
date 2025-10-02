package domain

type Todo struct {
	ID        int    `json:"id"`
	Title     string `json:"title"`
	Completed bool   `json:"completed"`
}

type UpdateTodoParam struct {
	ID        int  `json:"id"`
	Completed bool `json:"completed"`
}

type ListTodoParam struct {
	Page    int64 `json:"page"`
	PerPage int64 `json:"per_page"`
}
