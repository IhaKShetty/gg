import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { LivecheckModule } from './livecheck/livecheck.module';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ThreatsModule } from './threats/threats.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    TypeOrmModule.forRoot({
  type: 'postgres',
  host: 'localhost',
  port: 5432,
  username: 'postgres',
  password: 'S20vsdk76!$', // Hardcode temporarily
  database: 'threat_intel',
  entities: [__dirname + '/**/*.entity{.ts,.js}'],
  synchronize: true,
  logging: true,
}),
   
    LivecheckModule,
   
   
   
    ThreatsModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}