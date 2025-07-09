import { Controller, Get, Query, Param, ParseIntPipe } from '@nestjs/common';
import { ThreatsService } from './threat.service';
import { ThreatQueryDto } from './dto/theory-query.dto';

@Controller('/threats')
export class ThreatsController {
  constructor(private readonly threatsService: ThreatsService) {}

  @Get()
  async findAll(@Query() query: ThreatQueryDto) {
    return this.threatsService.findAll(query);
  }

  @Get(':id')
  async findOne(@Param('id', ParseIntPipe) id: number) {
    return this.threatsService.findOne(id);
  }

  @Get('stats')
  async getStats() {
    return this.threatsService.getStats();
  }
}