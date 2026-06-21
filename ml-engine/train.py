import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
from sklearn.preprocessing import LabelEncoder

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

# Load data from MySQL
def load_data():
    print("Loading data from MySQL...")
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM campaigns", conn)
    conn.close()
    print(f"Loaded {len(df)} rows")
    return df

# Prepare features
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

    # Save encoders
    joblib.dump(le_platform, 'ml-engine/le_platform.pkl')
    joblib.dump(le_campaign, 'ml-engine/le_campaign.pkl')
    joblib.dump(le_industry, 'ml-engine/le_industry.pkl')
    joblib.dump(le_country, 'ml-engine/le_country.pkl')

    features = ['platform_enc', 'campaign_type_enc', 'industry_enc',
                'country_enc', 'impressions', 'clicks', 'CTR',
                'CPC', 'ad_spend', 'conversions', 'CPA']

    return df, features

# Train ROI Prediction Model
def train_roi_model(df, features):
    print("\n Training ROI Prediction Model...")
    X = df[features]
    y = df['ROI']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"ROI Model - MAE: {mae:.2f} | R2 Score: {r2:.4f}")

    joblib.dump(model, 'ml-engine/roi_model.pkl')
    print("ROI model saved!")
    return model

# Train Campaign Success Model
def train_success_model(df, features):
    print("\n Training Campaign Success Model...")
    df['success'] = (df['ROI'] > 100).astype(int)

    X = df[features]
    y = df['success']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Success Model - Accuracy: {acc*100:.2f}%")

    joblib.dump(model, 'ml-engine/success_model.pkl')
    print("Success model saved!")
    return model

# Recommendation Engine
def recommend_platform(roi):
    if roi > 700:
        return "TikTok Ads"
    elif roi > 400:
        return "Meta Ads"
    else:
        return "Google Ads"

if __name__ == "__main__":
    print("=== AdGenius AI - ML Training ===")
    df = load_data()
    df, features = prepare_features(df)
    train_roi_model(df, features)
    train_success_model(df, features)
    print("\n=== Training Complete! ===")
    print("Models saved in ml-engine/ folder")