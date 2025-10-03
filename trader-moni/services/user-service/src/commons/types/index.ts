export interface ServiceConfig {
  serviceName: string;
  healthCheckPath: string;
  version: string;
  tags: string[];
  port?: number; // Optional as it might come from the server
}

export interface NotificationPayload {
  userId: string;
  type: 'email' | 'sms' | 'push';
  category: string;
  recipient: string;
  message: string;
  metadata?: Record<string, any>;
  createdAt: string;
  recipients?: string[];
}

export enum OtpPurpose {
  ADMIN_LOGIN = 'ADMIN_LOGIN',
  ADMIN_RESET_PASSWORD = 'ADMIN_RESET_PASSWORD',
  ADMIN_INVITATION = 'ADMIN_INVITATION',
}
