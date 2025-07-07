import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { LivecheckModule } from './livecheck/livecheck.module';
@Module({
  imports: [ LivecheckModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
