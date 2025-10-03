import { Module } from '@nestjs/common';
import { HealthModule } from './health/health.module';
import { UsersController } from './users/users.controller';
import { UsersService } from './users/users.service';

@Module({
  imports: [HealthModule],
  controllers: [UsersController],
  providers: [UsersService]
})
export class ApiModule {}
