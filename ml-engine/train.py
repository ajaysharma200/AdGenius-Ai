import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
import joblib
import numpy as np
from xgboost import XGBRegressor, XGBClassifier
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )

def load_data():
    print("Loading data from MySQL...")
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM campaigns", conn)
    conn.close()
    print(f"Loaded {len(df)} rows")
    return df

def prepare_features(df):
    print("Preparing features...")
    le_platform = LabelEncoder()
    le_campaign = LabelEncoder()
    le_industry = LabelEncoder()
    le_country = LabelEncoder()

    df['platform_enc'] = le_platform.fit_transform(df['platform'])
    df['campaign_type_enc'] = le_campaign.fit_transform(df['campaign_type'])
    df['industry_enc'] = le_industry.fit_transform(df['industry'])
    df['country_enc'] = le_country.fit_transform(df['country'])

    joblib.dump(le_platform, 'ml-engine/le_platform.pkl')
    joblib.dump(le_campaign, 'ml-engine/le_campaign.pkl')
    joblib.dump(le_industry, 'ml-engine/le_industry.pkl')
    joblib.dump(le_country, 'ml-engine/le_country.pkl')

    features = ['platform_enc', 'campaign_type_enc', 'industry_enc',
                'country_enc', 'impressions', 'clicks', 'CTR',
                'CPC', 'ad_spend', 'conversions', 'CPA']
    return df, features

def train_roi_model(df, features):
    print("\n Training XGBoost ROI Prediction Model...")
    X = df[features]
    y = df['ROI']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42, verbosity=0)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"XGBoost ROI Model - MAE: {mae:.2f} | R2 Score: {r2:.4f}")
    joblib.dump(model, 'ml-engine/roi_model.pkl')
    print("ROI model saved!")

def train_success_model(df, features):
    print("\n Training XGBoost Campaign Success Model...")
    df['success'] = (df['ROI'] > 100).astype(int)

    X = df[features]
    y = df['success']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42, verbosity=0)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"XGBoost Success Model - Accuracy: {acc*100:.2f}%")

    joblib.dump(model, 'ml-engine/success_model.pkl')
    print("Success model saved!")

def train_segmentation_model(df):
    print("\n Training KMeans Customer Segmentation...")
    seg_features = ['ad_spend', 'impressions', 'clicks', 'conversions', 'ROI']
    X = df[seg_features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['segment'] = kmeans.fit_predict(X_scaled)

    segment_roi = df.groupby('segment')['ROI'].mean().sort_values(ascending=False)
    segment_map = {}
    labels = ['High Value', 'Medium Value', 'Low Value']
    for i, seg in enumerate(segment_roi.index):
        segment_map[seg] = labels[i]

    df['segment_label'] = df['segment'].map(segment_map)

    print("Segment Distribution:")
    print(df['segment_label'].value_counts())

    joblib.dump(kmeans, 'ml-engine/kmeans_model.pkl')
    joblib.dump(scaler, 'ml-engine/scaler.pkl')
    print("Segmentation model saved!")

if __name__ == "__main__":
    print("=== AdGenius AI - ML Training ===")
    df = load_data()
    df, features = prepare_features(df)
    train_roi_model(df, features)
    train_success_model(df, features)
    train_segmentation_model(df)
    print("\n=== All Models Training Complete! ===")
    print("  roi_model.pkl      -> XGBoost ROI Prediction")
    print("  success_model.pkl  -> XGBoost Classifier")
    print("  kmeans_model.pkl   -> KMeans Segmentation")
    print("  scaler.pkl         -> StandardScaler")