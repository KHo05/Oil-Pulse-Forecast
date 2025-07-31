from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime
import os, logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _load_csv(path, **kwargs):
    try:
        return pd.read_csv(path, **kwargs)
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise HTTPException(500, f"{os.path.basename(path)} not found")
    except Exception as e:
        logger.error(f"Error loading {path}: {str(e)}")
        raise HTTPException(500, str(e))

def _to_naive(dt_series):
    if pd.api.types.is_datetime64tz_dtype(dt_series):
        return dt_series.dt.tz_localize(None)
    return dt_series

def _load_ts(path, **kwargs):
    try:
        return pd.read_csv(path, index_col=0, parse_dates=True, **kwargs).rename_axis("date")
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise HTTPException(500, f"{os.path.basename(path)} not found")
    except Exception as e:
        logger.error(f"Error loading {path}: {str(e)}")
        raise HTTPException(500, str(e))

def _convert_to_float(df, columns):
    """Convert specified columns to float with NaN handling"""
    for col in columns:
        if col in df.columns:
            # Replace non-numeric values and convert
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Replace NaN with 0 for proper JSON serialization
            df[col] = df[col].fillna(0)
    return df

# -------------------------------------------------
# End-points
# -------------------------------------------------
@app.get("/predictions")
def get_predictions(start: str = None, end: str = None):
    try:
        df = _load_ts(os.path.join(DATA_DIR, "bigru_predictions.csv")).reset_index()
        logger.info(f"Loaded predictions data. Initial shape: {df.shape}")
        
        # Convert date and numeric columns
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = _convert_to_float(df, ["Actual", "Predicted"])
        
        # Drop rows with invalid dates or null numeric values
        df = df.dropna(subset=["date", "Actual", "Predicted"])
        logger.info(f"After date cleaning: {df.shape}")
        
        # Filter by date range
        if start and end:
            try:
                s = pd.to_datetime(start)
                e = pd.to_datetime(end)
                df = df[(df["date"] >= s) & (df["date"] <= e)]
                logger.info(f"After date filtering: {df.shape}")
            except Exception as e:
                logger.error(f"Date filtering error: {str(e)}")
        
        # Final cleanup and serialization
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        
        logger.info(f"Returning {len(df)} prediction records")
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Prediction endpoint failed: {str(e)}")
        raise HTTPException(500, "Failed to process prediction data")

@app.get("/sentiment")
def get_sentiment(start: str = None, end: str = None):
    try:
        df = _load_csv(os.path.join(DATA_DIR, "sentiment_scores.csv"))
        logger.info(f"Loaded sentiment data. Initial shape: {df.shape}")
        
        # Convert date and numeric columns
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = _convert_to_float(df, ["sentiment"])
        
        # Drop rows with invalid dates or null sentiment
        df = df.dropna(subset=["date", "sentiment"])
        logger.info(f"After cleaning: {df.shape}")
        
        # Filter by date range
        if start and end:
            try:
                s = pd.to_datetime(start)
                e = pd.to_datetime(end)
                df = df[(df["date"] >= s) & (df["date"] <= e)]
                logger.info(f"After date filtering: {df.shape}")
            except Exception as e:
                logger.error(f"Date filtering error: {str(e)}")
        
        # Final serialization
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        
        logger.info(f"Returning {len(df)} sentiment records")
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Sentiment endpoint failed: {str(e)}")
        raise HTTPException(500, "Failed to process sentiment data")

@app.get("/news")
def get_news(start: str = None, end: str = None, limit: int = 5):
    try:
        df = _load_csv(os.path.join(DATA_DIR, "news_articles.csv"))
        logger.info(f"Loaded news data. Initial shape: {df.shape}")
        
        # Convert and clean dates
        df["publishedAt"] = pd.to_datetime(df["publishedAt"], utc=True, errors='coerce').pipe(_to_naive)
        df = df.dropna(subset=["publishedAt"])
        logger.info(f"After date cleaning: {df.shape}")
        
        # Filter by date range
        if start and end:
            try:
                s = pd.to_datetime(start)
                e = pd.to_datetime(end)
                df = df[(df["publishedAt"] >= s) & (df["publishedAt"] <= e)]
                logger.info(f"After date filtering: {df.shape}")
            except Exception as e:
                logger.error(f"Date filtering error: {str(e)}")
        
        # Sort and limit
        df = df.sort_values("publishedAt", ascending=False).head(limit)
        df["publishedAt"] = df["publishedAt"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        logger.info(f"Returning {len(df)} news records")
        return df[["title", "description", "publishedAt"]].to_dict(orient="records")
    except Exception as e:
        logger.error(f"News endpoint failed: {str(e)}")
        raise HTTPException(500, "Failed to process news data")

@app.get("/")
def health_check():
    return {"status": "active"}