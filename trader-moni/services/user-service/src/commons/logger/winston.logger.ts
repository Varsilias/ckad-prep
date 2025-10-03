import { WinstonModule } from 'nest-winston';
import * as winston from 'winston';

export const WinstonLogger = WinstonModule.createLogger({
  transports: [
    new winston.transports.Console({
      level: process.env.NODE_ENV === 'development' ? 'debug' : 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        // winston.format.prettyPrint(),
        winston.format.colorize(),
        winston.format.printf(
          ({ timestamp, level, message, context }) =>
            `${timestamp} [${level}] ${message} ${context}`,
        ),
      ),
    }),
    // new winston.transports.File({
    //   filename: process.env.LOG_FILE || 'logs/user-service.log', // Set log file path
    //   level: process.env.NODE_ENV === 'development' ? 'debug' : 'info',
    //   format: winston.format.combine(
    //     winston.format.timestamp(),
    //     winston.format.json(),
    //     // winston.format.printf(
    //     //   ({ timestamp, level, message, context }) =>
    //     //     `${timestamp} [${level}] ${message} ${context}`,
    //     // ),
    //   ),
    // }),
  ],
});
