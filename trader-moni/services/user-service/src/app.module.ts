import { MiddlewareConsumer, Module, NestModule } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { ServicesModule } from './commons/services/services.module';
import { ConfigModule } from '@nestjs/config';
import {
  determineEnvFilePath,
  envValidationSchema,
} from './commons/utils/env.utils';
import { RequestLoggerMiddleware } from './commons/middlewares/request-logger.middleware';
import { ApiModule } from './api/api.module';

@Module({
  imports: [
    ServicesModule,
    ConfigModule.forRoot({
      isGlobal: true, // Makes the ConfigModule globally available
      envFilePath: determineEnvFilePath(), // Dynamically load the correct `.env` file
      validationSchema: envValidationSchema,
      validationOptions: {
        allowUnknown: true, // Prevent unknown keys in .env files
        abortEarly: true, // Stop validation on the first error
      },
    }),
    ApiModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(RequestLoggerMiddleware).forRoutes('*');
  }
}
