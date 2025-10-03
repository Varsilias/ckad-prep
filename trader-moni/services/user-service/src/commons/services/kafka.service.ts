import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Kafka, Partitioners } from 'kafkajs';
import { NotificationPayload } from '../types';
import { Logger } from '@nestjs/common';

@Injectable()
export class KafkaService {
  private readonly kafka: Kafka;
  private readonly logger = new Logger(KafkaService.name);

  constructor(private readonly configService: ConfigService) {
    this.kafka = new Kafka({
      clientId: this.configService.get('KAFKA_CLIENT_ID'),
      brokers: [this.configService.get('KAFKA_BROKER') as string],
    });
  }

  async sendMessage(payload: NotificationPayload) {
    if (this.configService.get('NODE_ENV') === 'test') {
      this.logger.log('Kafka is disabled in test environment');
      return;
    }
    const topic = this.configService.get('KAFKA_TOPIC').split(',');
    const producer = this.kafka.producer({
      createPartitioner: Partitioners.LegacyPartitioner,
    });
    await producer.connect();
    this.logger.log(
      `Sending message to Kafka: ${[
        ...(payload?.recipients || []),
        payload?.recipient,
      ]
        .filter(Boolean)
        .join(', ')}`,
    );

    for (const t of topic) {
      if (t.includes(payload.type)) {
        await producer.send({
          topic: t,
          messages: [{ value: JSON.stringify(payload) }],
        });
      }
    }
  }
}
