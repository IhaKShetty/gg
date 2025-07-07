import { Module } from '@nestjs/common';
import { livecheckController } from './livecheck.controller';
import { livecheckService } from './livecheck.service';

@Module({
  controllers: [livecheckController],
  providers: [livecheckService],
})
export class LivecheckModule {}
