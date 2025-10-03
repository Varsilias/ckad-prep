export class PaginationMetaDto {
  readonly total_items: number;
  readonly item_count: number;
  readonly items_per_page: number;
  readonly total_pages: number;
  readonly current_page: number;

  constructor({
    total_items,
    item_count,
    items_per_page,
    total_pages,
    current_page,
  }: PaginationMetaDto) {
    this.total_items = total_items;
    this.item_count = item_count;
    this.items_per_page = items_per_page;
    this.total_pages = total_pages;
    this.current_page = current_page;
  }
}

export class PaginationResponseDto<T> {
  readonly records: T[];
  readonly meta: PaginationMetaDto;

  constructor(records: T[], meta: PaginationMetaDto) {
    this.records = records;
    this.meta = meta;
  }
}
