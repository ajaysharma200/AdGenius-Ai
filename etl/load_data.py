import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
 
load_dotenv()
 
# Database Connection
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )
 
# Extract
def extract(filepath):
    print("Extracting data...")
    df = pd.read_csv(filepath)
    print(f"Rows loaded: {len(df)}")
    return df
 
# Transform
def transform(df):
    print("Transforming data...")
    df.columns = df.columns.str.strip().str.lower()
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['roi'] = ((df['revenue'] - df['ad_spend']) / df['ad_spend']) * 100
    df['roi'] = df['roi'].round(2)
    df = df.dropna()
    print(f"Rows after cleaning: {len(df)}")
    return df
 
# Load
def load(df):
    print("Loading data into MySQL...")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM campaigns")
    inserted = 0
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO campaigns 
            (date, platform, campaign_type, industry, country,
             impressions, clicks, CTR, CPC, ad_spend,
             conversions, CPA, revenue, ROAS, ROI)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            row['date'], row['platform'], row['campaign_type'],
            row['industry'], row['country'], int(row['impressions']),
            int(row['clicks']), float(row['ctr']), float(row['cpc']),
            float(row['ad_spend']), int(row['conversions']),
            float(row['cpa']), float(row['revenue']),
            float(row['roas']), float(row['roi'])
        ))
        inserted += 1
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Successfully inserted {inserted} rows!")
 
# Run ETL
if __name__ == "__main__":
    print("=== AdGenius AI - ETL Pipeline ===")
    df = extract("datasets/ads_data.csv")
    df = transform(df)
    load(df)
    print("=== ETL Complete! ===")