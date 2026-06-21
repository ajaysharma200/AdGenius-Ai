from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import get_db_connection
import joblib
import numpy as np
import pandas as pd

app = FastAPI(title="AdGenius AI API", version="1.0.0")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML Models
roi_model = joblib.load("ml-engine/roi_model.pkl")
success_model = joblib.load("ml-engine/success_model.pkl")
le_platform = joblib.load("ml-engine/le_platform.pkl")
le_campaign = joblib.load("ml-engine/le_campaign.pkl")
le_industry = joblib.load("ml-engine/le_industry.pkl")
le_country = joblib.load("ml-engine/le_country.pkl")

# Recommendation Engine
def recommend_platform(roi):
    if roi > 700:
        return "TikTok Ads"
    elif roi > 400:
        return "Meta Ads"
    else:
        return "Google Ads"

@app.get("/")
def root():
    return {"message": "AdGenius AI API is running!", "version": "1.0.0"}

@app.get("/analytics")
def get_analytics():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as total_campaigns FROM campaigns")
    total = cursor.fetchone()

    cursor.execute("SELECT ROUND(SUM(ad_spend), 2) as total_spend FROM campaigns")
    spend = cursor.fetchone()

    cursor.execute("SELECT ROUND(SUM(revenue), 2) as total_revenue FROM campaigns")
    revenue = cursor.fetchone()

    cursor.execute("SELECT ROUND(AVG(ROI), 2) as avg_roi FROM campaigns")
    roi = cursor.fetchone()

    cursor.execute("""
        SELECT platform, COUNT(*) as campaigns, 
               ROUND(AVG(ROI), 2) as avg_roi,
               ROUND(SUM(ad_spend), 2) as total_spend,
               ROUND(SUM(revenue), 2) as total_revenue
        FROM campaigns GROUP BY platform
    """)
    platforms = cursor.fetchall()

    cursor.execute("""
        SELECT industry, ROUND(AVG(ROI), 2) as avg_roi,
               COUNT(*) as campaigns
        FROM campaigns GROUP BY industry
        ORDER BY avg_roi DESC
    """)
    industries = cursor.fetchall()

    cursor.execute("""
        SELECT DATE_FORMAT(date, '%Y-%m') as month,
               ROUND(AVG(ROI), 2) as avg_roi,
               ROUND(SUM(ad_spend), 2) as total_spend
        FROM campaigns GROUP BY month ORDER BY month
    """)
    trends = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total_campaigns": total["total_campaigns"],
        "total_spend": spend["total_spend"],
        "total_revenue": revenue["total_revenue"],
        "avg_roi": roi["avg_roi"],
        "platform_performance": platforms,
        "industry_performance": industries,
        "monthly_trends": trends
    }

@app.post("/predict")
def predict_roi(data: dict):
    try:
        platform_enc = le_platform.transform([data["platform"]])[0]
        campaign_enc = le_campaign.transform([data["campaign_type"]])[0]
        industry_enc = le_industry.transform([data["industry"]])[0]
        country_enc = le_country.transform([data["country"]])[0]

        features = np.array([[
            platform_enc, campaign_enc, industry_enc, country_enc,
            data["impressions"], data["clicks"], data["CTR"],
            data["CPC"], data["ad_spend"], data["conversions"], data["CPA"]
        ]])

        predicted_roi = roi_model.predict(features)[0]
        success = success_model.predict(features)[0]
        recommended = recommend_platform(predicted_roi)

        return {
            "predicted_roi": round(float(predicted_roi), 2),
            "campaign_success": bool(success),
            "recommended_platform": recommended,
            "confidence": "High" if abs(predicted_roi) > 100 else "Medium"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/campaigns")
def get_campaigns(limit: int = 50):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM campaigns ORDER BY id DESC LIMIT {limit}")
    campaigns = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"campaigns": campaigns, "total": len(campaigns)}

@app.get("/segmentation")
def get_segmentation():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT platform, industry, country,
               ROUND(AVG(ROI), 2) as avg_roi,
               ROUND(AVG(ad_spend), 2) as avg_spend,
               COUNT(*) as total
        FROM campaigns
        GROUP BY platform, industry, country
        ORDER BY avg_roi DESC
        LIMIT 20
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"segmentation": data}