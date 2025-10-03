import * as fs from 'fs';
import * as Joi from 'joi';
import * as crypto from 'crypto';

export function determineEnvFilePath(): string {
  const env = process.env.NODE_ENV || 'development';
  const envFilePath =
    env !== 'development'
      ? `${process.cwd()}/.env.${env}`
      : `${process.cwd()}/.env`;

  if (!fs.existsSync(envFilePath)) {
    throw new Error(`Environment file not found: ${envFilePath}`);
  }

  console.log(`Using environment file: ${envFilePath}`);

  return envFilePath;
}

export const envValidationSchema = Joi.object({
  NODE_ENV: Joi.string()
    .valid('development', 'test', 'staging', 'production', 'venus')
    .required(),
  PORT: Joi.number().required(),
  SERVICE_NAME: Joi.string().required(),
  SERVICE_VERSION: Joi.string().required(),

  REDIS_HOST: Joi.string().required(),
  REDIS_PORT: Joi.number().required(),
  REDIS_PASSWORD: Joi.string().allow('').optional(),
  REDIS_URL: Joi.string().allow('').optional(),
});

export const hashToken = (str: string) => {
  return crypto.createHash('sha256').update(str).digest('hex');
};

export const compareToken = (str: string, hashedToken: string) => {
  return hashToken(str) === hashedToken;
};

export const generateSixDigitNumber = () => {
  // Generate a random number between 0 and 999999
  const randomInt = Math.floor(Math.random() * 1000000);

  // Ensure the number is always 6 digits by padding with leading zeros if necessary
  return randomInt.toString().padStart(6, '0');
};

export const generateExpiresIn = (expiresIn: string) => {
  const timeUnit = expiresIn.slice(-1);
  const timeValue = parseInt(expiresIn.slice(0, -1), 10);

  switch (timeUnit) {
    case 'm':
      return timeValue * 60;
    case 'h':
      return timeValue * 60 * 60;
    case 'd':
      return timeValue * 24 * 60 * 60;
    default:
      return parseInt(expiresIn, 10);
  }
};

/**
 * Capitalizes the first letter of each word in an array of strings
 * @param words - Array of strings to capitalize
 * @returns Array of strings with first letter capitalized
 * @example
 * capitaliseWords(['hello', 'world']) // ['Hello', 'World']
 */
export const capitaliseWords = (words: string[]) => {
  return words.map((word) => {
    const firstChar = word[0];
    return firstChar.toUpperCase() + word.slice(1);
  });
};
