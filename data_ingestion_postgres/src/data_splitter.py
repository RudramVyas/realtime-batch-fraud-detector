import pandas as pd
import os


FULL_LOAD_PERCENT = 0.60
INCREMENTAL_LOAD_PERCENT = 0.20
KAFKA_STREAMING_PERCENT = 0.20

# Main function
def main():
    input_file = 'data/raw/synthetic_fraud_dataset.csv' 
    output_dir = 'data/split'
    os.makedirs(output_dir, exist_ok=True)


    df = pd.read_csv(input_file).sort_values(by='Timestamp', ascending=True)
    total_rows = len(df)

    
    full_end = int(total_rows * FULL_LOAD_PERCENT)
    incremental_end = full_end + int(total_rows * INCREMENTAL_LOAD_PERCENT)

    
    
    df_full = df.iloc[:full_end]
    df_incremental = df.iloc[full_end:incremental_end]
    df_kafka = df.iloc[incremental_end:]

    
    df_full.to_csv(f'{output_dir}/full_load.csv', index=False)
    df_incremental.to_csv(f'{output_dir}/incremental_load.csv', index=False)
    df_kafka.to_csv(f'{output_dir}/kafka_streaming.csv', index=False)


    print("CSV Split Completed:")
    print(f" - Full Load ({FULL_LOAD_PERCENT * 100:.0f}%): {len(df_full)} rows")
    print(f" - Incremental Load ({INCREMENTAL_LOAD_PERCENT * 100:.0f}%): {len(df_incremental)} rows")
    print(f" - Kafka Streaming ({KAFKA_STREAMING_PERCENT * 100:.0f}%): {len(df_kafka)} rows")


if __name__ == "__main__":
    main()
