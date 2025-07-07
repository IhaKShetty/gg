import { Entity, PrimaryGeneratedColumn, Column, Index } from 'typeorm';

@Entity('threats')
export class Threat {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  threat_category: string;

  @Column('simple-array', { nullable: true })
  iocs: string[];

  @Column({ nullable: true })
  threat_actor: string;

  @Column({ nullable: true })
  attack_vector: string;

  @Column({ nullable: true })
  geographical_location: string;

  @Column('float', { nullable: true })
  sentiment_in_forums: number;

  @Column('int')
  @Index()
  severity_score: number;

  @Column({ nullable: true })
  predicted_threat_category: string;

  @Column({ nullable: true })
  suggested_defense_mechanism: string;

  @Column('int', { nullable: true })
  risk_level_prediction: number;

  @Column('text', { nullable: true })
  @Index({ fulltext: true })
  cleaned_threat_description: string|null;

  @Column('simple-array', { nullable: true })
  keyword_extraction: string[];

  @Column('simple-array', { nullable: true })
  named_entities_ner: string[];

  @Column({ nullable: true })
  topic_modeling_labels: string;

  @Column('int', { nullable: true })
  word_count: number;
}