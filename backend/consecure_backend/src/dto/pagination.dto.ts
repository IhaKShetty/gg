import { IsInt, IsOptional, IsString, Min } from 'class-validator';

export class paginationDto {
  @IsOptional()
  @IsInt({ message: 'Page number should be an integer' })
  @Min(1, { message: 'Page must be at least 1' })
  page?: number = 1;

  @IsOptional()
  @IsInt({ message: 'Limit should be an integer' })
  @Min(1, { message: 'Limit must be at least 1' })
  limit?: number = 20;

  @IsOptional()
  @IsString({ message: 'Category must be a string' })
  category?: string;

  @IsOptional()
  @IsString()
  serach?: string;
}
