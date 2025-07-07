import os
from dotenv import load_dotenv
import argparse
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import json
import re
import sys
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "threat_intel"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

def create_tables(conn):
    """Create tables if they don't exist"""
    with conn.cursor() as cursor:
        # Create threats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id SERIAL PRIMARY KEY,
                threat_category TEXT NOT NULL,
                threat_actor TEXT,
                attack_vector TEXT,
                geographical_location TEXT,
                sentiment_in_forums FLOAT,
                severity_score INTEGER CHECK (severity_score BETWEEN 1 AND 5),
                predicted_threat_category TEXT,
                suggested_defense_mechanism TEXT,
                risk_level_prediction INTEGER CHECK (risk_level_prediction BETWEEN 1 AND 5),
                iocs JSONB
            );
        """)

        # Create NLP features table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threat_nlp_features (
                id SERIAL PRIMARY KEY,
                threat_id INTEGER REFERENCES threats(id) ON DELETE CASCADE,
                cleaned_threat_description TEXT,
                keywords TEXT[],
                named_entities TEXT[],
                topic_modeling_labels TEXT[],
                word_count INTEGER
            );
        """)
        conn.commit()

def parse_iocs(ioc_string):
    """Convert IOC string to proper JSON array"""
    if pd.isna(ioc_string) or not ioc_string:
        return []

    try:
        cleaned = ioc_string.strip()
        if cleaned.startswith('[') and cleaned.endswith(']'):
            return json.loads(cleaned)
        elif cleaned.startswith("['") or cleaned.startswith('["'):
            cleaned = cleaned.replace("'", '"')
            return json.loads(cleaned)
        elif ',' in cleaned:
            return [item.strip() for item in cleaned.split(',')]
        elif ' ' in cleaned:
            return [item.strip() for item in cleaned.split()]
        else:
            return [cleaned]
    except (json.JSONDecodeError, TypeError):
        cleaned = re.sub(r'[\[\]\'"]', '', ioc_string)
        return [item.strip() for item in cleaned.split(',') if item.strip()]

def validate_scores(row):
    """Ensure scores are within valid ranges"""
    sentiment = float(row.get('Sentiment in Forums', 0.5))
    sentiment = max(0.5, min(1.0, sentiment))

    severity = int(row.get('Severity Score', 1))
    severity = max(1, min(5, severity))

    risk = int(row.get('Risk Level Prediction', 1))
    risk = max(1, min(5, risk))

    return sentiment, severity, risk

def ingest_data(csv_path):
    """Main ingestion function"""
    start_time = datetime.now()
    print(f"\nStarting ingestion at {start_time}")

    # Verify file exists
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found at {csv_path}")
        print("Current directory:", os.getcwd())
        print("Try using absolute path like: C:\\Users\\you\\Downloads\\file.csv")
        return

    # Read CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded CSV with {len(df)} records and {len(df.columns)} columns")
        print("Columns detected:", list(df.columns))
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return

    # Connect to PostgreSQL
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        create_tables(conn)

        with conn.cursor() as cursor:
            # Prepare data storage
            threat_data = []
            nlp_data = []

            # Process each row
            for index, row in df.iterrows():
                sentiment, severity, risk = validate_scores(row)
                iocs = parse_iocs(row.get('IOCs (Indicators of Compromise)', ''))

                threat_record = (
                    row.get('Threat Category', ''),
                    json.dumps(iocs),  # Convert to JSON string
                    row.get('Threat Actor', ''),
                    row.get('Attack Vector', ''),
                    row.get('Geographical Location', ''),
                    sentiment,
                    severity,
                    row.get('Predicted Threat Category', ''),
                    row.get('Suggested Defense Mechanism', ''),
                    risk
                )
                threat_data.append(threat_record)

                # Prepare NLP data if available
                if 'Cleaned Threat Description' in row and pd.notna(row['Cleaned Threat Description']):
                    nlp_record = (
                        row.get('Cleaned Threat Description', ''),
                        row.get('Keyword Extraction', '').split(';') if pd.notna(row.get('Keyword Extraction')) else [],
                        row.get('Named Entities (NER)', '').split(';') if pd.notna(row.get('Named Entities (NER)')) else [],
                        row.get('Topic Modeling Labels', '').split(',') if pd.notna(row.get('Topic Modeling Labels')) else [],
                        int(row.get('Word Count', 0)) if pd.notna(row.get('Word Count')) else 0
                    )
                    nlp_data.append(nlp_record)
                else:
                    nlp_data.append(None)

            # Insert threats using individual inserts to get generated IDs
            threat_ids = []
            threat_insert_query = """
        INSERT INTO threats (
            threat_category, iocs, threat_actor, attack_vector,
            geographical_location, sentiment_in_forums, severity_score,
            predicted_threat_category, suggested_defense_mechanism, risk_level_prediction
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
            threat_insert_query = " ".join(line.strip() for line in threat_insert_query.splitlines()).strip()
    
            threat_ids = []
            for record in threat_data:
                cursor.execute(threat_insert_query, record)
                threat_id = cursor.fetchone()[0]
                threat_ids.append(threat_id)
            print(f"Inserted {len(threat_ids)} threat records")

            

            # Insert NLP features
            nlp_insert_query = """
    INSERT INTO threat_nlp_features (
        threat_id, cleaned_threat_description, keywords, 
        named_entities, topic_modeling_labels, word_count
    ) VALUES %s
"""

            nlp_records = []
            for threat_id, nlp_record in zip(threat_ids, nlp_data):
                if nlp_record is not None:
                    # Only include records with NLP data
                    nlp_records.append((
                        threat_id,
                        nlp_record[0],
                        nlp_record[1],
                        nlp_record[2],
                        nlp_record[3],
                        nlp_record[4]
                    ))

            if nlp_records:
                execute_values(
                    cursor,
                    nlp_insert_query,
                    nlp_records,
                    template=None,
                    page_size=100
                )
                print(f"Inserted {len(nlp_records)} NLP records")
            else:
                print("No valid NLP features to insert")

        conn.commit()
        duration = datetime.now() - start_time
        print(f"\n✅ Ingestion completed successfully in {duration.total_seconds():.2f} seconds")
        print(f"Total threats: {len(threat_data)}")
        if nlp_records:
            print(f"Total NLP records: {len(nlp_records)}")

    except psycopg2.Error as e:
        print(f"Database error: {str(e)}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ingest cyber threat data into PostgreSQL')
    parser.add_argument('csv_path', help='Path to the CSV file')
    args = parser.parse_args()

    ingest_data(args.csv_path)