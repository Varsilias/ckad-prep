import { Controller, Get } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Controller('health')
export class HealthController {
  constructor(private readonly configService: ConfigService) {}

  @Get()
  getHealth() {
    return {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: this.configService.get('SERVICE_NAME') || 'user-service',
      version: this.configService.get('SERVICE_VERSION') || '1.0.0',
      environment: this.configService.get('NODE_ENV') || 'development',
    };
  }
}
