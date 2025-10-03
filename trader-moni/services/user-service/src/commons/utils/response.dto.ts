export class ResponseDto<T extends Record<string, any> = Record<string, any>> {
  status: boolean;
  message: string;
  data?: T;
  status_code?: number;
  constructor(
    status: boolean,
    message: string,
    data?: any,
    status_code?: number,
  ) {
    this.status = status;
    this.message = message;
    this.status_code = status_code;
    this.data = data;
  }

  static success<T>(message: string, data?: any, status_code?: number): T {
    return new ResponseDto(true, message, data, status_code) as T;
  }

  static failure<T>(message: string, data?: any, status_code: number = 400): T {
    return new ResponseDto(false, message, data, status_code) as T;
  }

  static internalServerError<T>(
    message: string,
    data?: any,
    status_code?: number,
  ): T {
    return new ResponseDto(false, message, data, status_code) as T;
  }
}
