#!/usr/bin/env python3.8

import os
import sys
import argparse
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote_plus

def load_environment(env_path: str = None):
    """
    Load environment variables from a .env file or system environment.
    """
    load_dotenv(dotenv_path=env_path)


def create_db_engine():
    """
    Create a SQLAlchemy engine using environment variables.
    Exits if required variables are missing or connection fails.
    """
    user = os.getenv("DB_USERNAME")
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")

    if not all([user, password, host, port, database]):
        print("One or more database environment variables are missing.")
        sys.exit(1)

    conn_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    try:
        engine = create_engine(conn_str, pool_pre_ping=True)
        print("Database engine created successfully.")
        return engine
    except SQLAlchemyError as e:
        print("Failed to create database engine.")
        sys.exit(1)


def full_load(engine, csv_path, table_name):
    """
    Perform a full load by reading the CSV and replacing the table in Postgres.
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"Read {len(df)} rows from {csv_path}.")
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        print(f"Full load complete: table '{table_name}' replaced.")
    except Exception as e:
        print("Full load failed.")
        print(f"Error: {e}")
        raise


def incremental_load(engine, csv_path, table_name):
    """
    Perform an incremental load by:
    - Getting the max Timestamp from the Postgre table
    - Filtering the CSV for rows with newer timestamps
    - Inserting only the top 1000 sorted by Timestamp
    """
    try:
        # Step 1: Get the max Timestamp from the DB table
        with engine.connect() as conn:
            result = conn.execute(text(f'SELECT MAX("Timestamp") FROM {table_name}'))
            max_ts = result.scalar() or datetime(1970, 1, 1)
            print(f"Max timestamp from DB: {max_ts}")
            
        # Step 2: Read CSV
        df = pd.read_csv(csv_path)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        print(f"Read {len(df)} rows from {csv_path}.")
        
        # Step 3: Filter and sort
        df_new = df[df['Timestamp'] > max_ts].sort_values(by='Timestamp').head(1000)
        
        if df_new.empty:
            print("No new records found for incremental load.")
            return
        
        # Step 4: Insert
        df_new.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        print(f"Incremental load complete: {len(df_new)} new rows added to '{table_name}'.")
        
    except Exception as e:
        print("Incremental load failed.")
        print(f"Error: {e}")
        raise

def stream_tbl_postgres(engine, csv_path, table_name):
    """
    Load streaming data (simulated Kafka) into a target Postgres table.
    Used for real-time table creation or updates.
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"Read {len(df)} rows from {csv_path}.")
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        print(f"Streaming table created: data appended to '{table_name}'.")
    except Exception as e:
        print("Streaming table not created.")
        print(f"Error: {e}")
        raise

def parse_args():
    """
    Parse command-line arguments for the ETL mode.
    Modes:
      - full: full load (replace table)
      - inc: incremental load (append only new data)
      - stream: streaming load (Kafka simulation) new table in postgres
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["full", "inc","stream"], help="Mode of ETL operation")
    return parser.parse_args()
    

def main():
    args = parse_args()
    load_environment()
    engine = create_db_engine()

    # Environment paths for the CSVs
    full_csv = os.getenv("FULL_LOAD_CSV", "../data/split/full_load.csv")
    inc_csv = os.getenv("INCREMENTAL_LOAD_CSV", "../data/split/incremental_load.csv")
    streaming_csv = os.getenv("KAFKA_STREAMING_CSV", "../data/split/kafka_streaming.csv")
    table = os.getenv("LOAD_TABLE", "cc_fraud_trans")

    try:
        if args.mode == "full":
            full_load(engine, full_csv, table)
        if args.mode == "inc":
            incremental_load(engine, inc_csv, table)
        if args.mode == "stream":
            stream_tbl_postgres(engine, streaming_csv, "cc_fraud_streaming_data")
    except Exception as e:
        print("ETL job failed.")
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        engine.dispose()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
