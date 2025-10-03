import { NestFactory, Reflector } from '@nestjs/core';
import { AppModule } from './app.module';
import { WinstonLogger } from './commons/logger/winston.logger';
import { ConfigService } from '@nestjs/config';
import {
  ClassSerializerInterceptor,
  Logger,
  ValidationPipe,
} from '@nestjs/common';
import { TransformInterceptor } from './commons/interceptors/response-transform.interceptor';
import { ParamValidationPipe } from './commons/pipes/param-validation.pipe';
import { GlobalExceptionFilter } from './commons/filters/global-exception.filter';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: WinstonLogger,
  });

  app.useGlobalPipes(
    new ValidationPipe({
      transform: true,
      stopAtFirstError: true,
    }),
  );

  app.useGlobalPipes(new ParamValidationPipe());

  app.useGlobalInterceptors(new TransformInterceptor());
  app.useGlobalFilters(new GlobalExceptionFilter());
  app.useGlobalInterceptors(new ClassSerializerInterceptor(app.get(Reflector)));

  const logger = new Logger('Bootstrap');

  const config = new ConfigService();

  const port = config.get<number>('PORT') || 3001;
  const serviceName = config.get('SERVICE_NAME') || 'user-service';
  const version = config.get('SERVICE_VERSION') || '1.0.0';

  await app.listen(port, () => {
    logger.log(`${serviceName} v${version} running on port ${port}`);
  });
}
bootstrap();
