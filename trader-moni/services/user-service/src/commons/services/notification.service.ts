import { Injectable } from '@nestjs/common';
import { NotificationPayload } from '../types';
import { KafkaService } from './kafka.service';

@Injectable()
export class NotificationService {
  constructor(private readonly kafkaService: KafkaService) {}

  async sendNotification(payload: NotificationPayload) {
    await this.kafkaService.sendMessage(payload);
  }

  async sendIdVerificationOtp(user: Record<string, any>, otp: number) {
    const payload: NotificationPayload = {
      userId: user.phone_number,
      type: 'sms',
      category: 'id_verification',
      recipient: user.phone_number,
      message: `Your ID Verification OTP is ${otp} \n\n Please do not share this OTP with anyone.`,
      metadata: {
        otp: otp,
        expiryTime: '10 minutes',
      },
      createdAt: new Date().toISOString(),
    };

    const emailPayload: NotificationPayload = {
      userId: user.email,
      type: 'email',
      category: 'id_verification',
      recipient: user.email,
      message: `Your ID Verification OTP is ${otp} \n\n Please do not share this OTP with anyone.`,
      metadata: {
        otp: otp,
        expiryTime: '10 minutes',
      },
      createdAt: new Date().toISOString(),
    };

    await Promise.all([
      this.sendNotification(payload),
      this.sendNotification(emailPayload),
    ]);
  }

  async sendForgotPasswordEmail(user: Record<string, any>, otp: number) {
    const payload: NotificationPayload = {
      userId: user.email,
      type: 'email',
      category: 'user_forgot_password',
      recipient: user.email,
      message: `Your One Time Password (OTP) is ${otp} \n\n Please do not share this OTP with anyone.`,
      metadata: {
        otp: otp,
        expiryTime: '10 minutes',
      },
      createdAt: new Date().toISOString(),
    };
    await this.sendNotification(payload);
  }

  async sendGetStartedEmail(user: Record<string, any>, otp: number) {
    const payload: NotificationPayload = {
      userId: user.email,
      type: 'email',
      category: 'get_started',
      recipient: user.email,
      message: 'Welcome to Chorus. Your Personal Financial Orchestrator',
      metadata: {
        otp: otp,
        expiryTime: '10 minutes',
      },
      createdAt: new Date().toISOString(),
    };
    await this.sendNotification(payload);
  }

  async sendGetStartedSms(user: Record<string, any>, otp: number) {
    const payload: NotificationPayload = {
      userId: user.phone_number,
      type: 'sms',
      category: 'get_started',
      recipient: user.phone_number,
      message: `Your One Time Password (OTP) is ${otp} \n\n Please do not share this OTP with anyone.`,
      metadata: {
        otp: otp,
        expiryTime: '10 minutes',
      },
      createdAt: new Date().toISOString(),
    };
    await this.sendNotification(payload);
  }

  async sendAnomalousActivityEmail(
    recipients: string[],
    activity: string,
    adminName: string,
    adminEmail: string,
    loginLink: string,
  ) {
    const payload: NotificationPayload = {
      userId: recipients[0],
      type: 'email',
      category: 'anomalous_activity',
      metadata: {
        activity: activity,
        adminName: adminName,
        adminEmail: adminEmail,
        loginLink: loginLink,
      },
      recipient: recipients[0],
      message: 'Anomalous Activity Detected',
      createdAt: new Date().toISOString(),
      recipients: recipients.slice(1), // for backwards compatibility
    };

    await this.sendNotification(payload);
  }

  async sendAccessLinkingOtp(user: Record<string, any>, otp: number) {
    const payload: NotificationPayload = {
      userId: user.phone_number,
      type: 'sms',
      category: 'access_linking',
      recipient: user.phone_number,
      message: `Your Access Linking OTP is ${otp} \n\n Please do not share this OTP with anyone.`,
      metadata: {
        otp: otp,
        expiryTime: '10 minutes',
      },
      createdAt: new Date().toISOString(),
    };

    const emailPayload: NotificationPayload = {
      userId: user.email,
      type: 'email',
      category: 'access_linking',
      recipient: user.email,
      message: `Your Access Linking OTP is ${otp} \n\n Please do not share this OTP with anyone.`,
      metadata: {
        otp: otp,
        expiryTime: '10 minutes',
      },
      createdAt: new Date().toISOString(),
    };

    await Promise.all([
      this.sendNotification(payload),
      this.sendNotification(emailPayload),
    ]);
  }
}
