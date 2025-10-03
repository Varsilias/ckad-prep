import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface Response {
  status: string;
  message: string;
  data: any;
}

@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, Response> {
  intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Observable<Response> {
    const code = context.switchToHttp().getResponse().statusCode;
    return next.handle().pipe(
      map((data) => {
        if (data && !data.code && typeof data !== 'string') {
          return { status: true, message: 'Request Successful', data };
        }

        if (typeof data === 'string' && !code.toString().startsWith('2')) {
          return { status: false, message: data };
        }

        return data;
      }),
    );
  }
}