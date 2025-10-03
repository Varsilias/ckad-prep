import { Global, Module } from '@nestjs/common';
import { TokenService } from './token.service';
import { JwtModule } from '@nestjs/jwt';
import { KafkaService } from './kafka.service';
import { NotificationService } from './notification.service';
import { HttpModule } from '@nestjs/axios';

@Global()
@Module({
  imports: [JwtModule, HttpModule],
  providers: [TokenService, KafkaService, NotificationService],
  exports: [TokenService, KafkaService, NotificationService],
})
export class ServicesModule {}
