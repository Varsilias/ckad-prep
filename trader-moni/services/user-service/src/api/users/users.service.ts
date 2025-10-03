import { Injectable } from '@nestjs/common';
import { CreateUserDto } from './dtos/create-user.dto';

@Injectable()
export class UsersService {
  async findAll() {}

  async findOne(id: string) {}

  async create(createUserDto: CreateUserDto) {}
}
