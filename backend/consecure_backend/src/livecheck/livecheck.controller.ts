import { Controller, Get } from '@nestjs/common';
import { livecheckService } from './livecheck.service';
@Controller()
export class livecheckController {
  constructor(private readonly livecheck: livecheckService) {}

  @Get('livecheck')
  getLivecheckStatus(): string {
    return this.livecheck.livecheckStatus();
  }
}
