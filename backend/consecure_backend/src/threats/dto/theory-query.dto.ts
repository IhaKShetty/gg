import { IsOptional, IsString, IsInt } from 'class-validator';
import { PaginationDto } from './pagination.dto';
export class ThreatQueryDto extends PaginationDto {
  @IsOptional()
  @IsString()
  category?: string;

  @IsOptional()
  @IsString()
  search?: string;
}