import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ThreatsController } from './threat.controller';
import { ThreatsService } from './threat.service';
import { Threat } from './threat.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Threat])],
  controllers: [ThreatsController],
  providers: [ThreatsService],
})
export class ThreatsModule {}