import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, ILike } from 'typeorm';
import { Threat } from './threat.entity';
import { ThreatQueryDto } from './dto/theory-query.dto'; // Fixed typo in filename

@Injectable()
export class ThreatsService {
  constructor(
    @InjectRepository(Threat)
    private readonly threatRepository: Repository<Threat>,
  ) {}

  async findAll(query: ThreatQueryDto) {
   const threats = await this.threatRepository.find({
      take: 10,
      order: { id: 'ASC' }, // Sort by ID ascending
    });

    return {
      data: threats,
    };
    

  }

  async findOne(id: number) {
    const threat = await this.threatRepository.findOne({ where: { id } });
    if (!threat) {
      throw new NotFoundException(`Threat with ID ${id} not found`);
    }
    return threat;
  }

  async getStats() {
    const total = await this.threatRepository.count();
    
    // Use entity property names in query builder
    const categoryStats = await this.threatRepository
      .createQueryBuilder('threat')
      .select('threat.threatCategory', 'category')
      .addSelect('COUNT(*)', 'count')
      .groupBy('threat.threatCategory')
      .getRawMany();

    const severityStats = await this.threatRepository
      .createQueryBuilder('threat')
      .select('threat.severityScore', 'severity')
      .addSelect('COUNT(*)', 'count')
      .groupBy('threat.severityScore')
      .orderBy('threat.severityScore', 'ASC')
      .getRawMany();

    return {
      total,
      byCategory: categoryStats,
      bySeverity: severityStats,
    };
  }
}