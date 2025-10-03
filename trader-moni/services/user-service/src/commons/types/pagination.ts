export type Pagination = {
  page: number;
  limit: number;
  sort: SortOrder;
  sort_by: string;
};

export type PaginationResponse<T> = {
  data: T[];
  total: number;
};

export enum SortOrder {
  ASC = 'ASC',
  DESC = 'DESC',
}

export enum RoleSortBy {
  NAME = 'name',
  TYPE = 'type',
  CREATED_AT = 'created_at',
  ID = 'id',
}

export enum PermissionSortBy {
  NAME = 'name',
  LEVEL = 'level',
  CREATED_AT = 'created_at',
  ID = 'id',
}

export enum InvitationSortBy {
  STATUS = 'status',
  CREATED_AT = 'created_at',
  ID = 'id',
}

export enum UnlockRequestSortBy {
  CREATED_AT = 'created_at',
  ID = 'id',
  REQUEST_DATE = 'request_date',
  LAST_ACTIVITY_DATE = 'last_activity_date',
}

export enum KycSortBy {
  CREATED_AT = 'created_at',
  ID = 'id',
  STATUS = 'status',
}

export enum CustomerSortBy {
  CREATED_AT = 'created_at',
  ID = 'id',
  STATUS = 'status',
}

export enum ChatSortBy {
  CREATED_AT = 'created_at',
  CLOSED_AT = 'closed_at',
  ID = 'id',
}
