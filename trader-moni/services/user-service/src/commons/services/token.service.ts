import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class TokenService {
  constructor(
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
  ) {}

  async signAccessToken(payload: { sub: string }) {
    return this.jwtService.signAsync(payload, {
      secret: this.configService.get('ADMIN_JWT_ACCESS_TOKEN_SECRET'),
      expiresIn: this.configService.get('ADMIN_JWT_ACCESS_TOKEN_EXPIRY'),
    });
  }

  async signRefreshToken(payload: { sub: string }) {
    return this.jwtService.signAsync(payload, {
      secret: this.configService.get('ADMIN_JWT_REFRESH_TOKEN_SECRET'),
      expiresIn: this.configService.get('ADMIN_JWT_REFRESH_TOKEN_EXPIRY'),
    });
  }

  async signPasswordResetToken(payload: {
    email: string;
    is_new_admin: boolean;
  }) {
    return this.jwtService.signAsync(payload, {
      secret: this.configService.get('ADMIN_RESET_PASSWORD_TOKEN_SECRET'),
      expiresIn: this.configService.get('ADMIN_RESET_PASSWORD_TOKEN_EXPIRY'),
    });
  }

  async signInvitationToken(
    payload: { sub: string },
    expiresIn: string | number,
  ) {
    return this.jwtService.signAsync(payload, {
      secret: this.configService.get('ADMIN_RESET_PASSWORD_TOKEN_SECRET'),
      expiresIn,
    });
  }

  async verifyPasswordResetToken(token: string) {
    return this.jwtService.verifyAsync(token, {
      secret: this.configService.get('ADMIN_RESET_PASSWORD_TOKEN_SECRET'),
      ignoreExpiration: false,
    });
  }
  async verifyAccessToken(accessToken: string) {
    return this.jwtService.verifyAsync(accessToken, {
      secret: this.configService.get('ADMIN_JWT_ACCESS_TOKEN_SECRET'),
    });
  }
  async verifyRefreshToken(refreshToken: string) {
    return this.jwtService.verifyAsync(refreshToken, {
      secret: this.configService.get('ADMIN_JWT_REFRESH_TOKEN_SECRET'),
    });
  }

  async verifyInvitationToken(invitationToken: string) {
    return this.jwtService.verifyAsync(invitationToken, {
      secret: this.configService.get('ADMIN_RESET_PASSWORD_TOKEN_SECRET'),
      ignoreExpiration: false,
    });
  }

  async decodePasswordResetToken(token: string) {
    return this.jwtService.decode(token);
  }
}
