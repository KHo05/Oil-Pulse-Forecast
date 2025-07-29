from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# Allow CORS for React front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predictions")
def get_predictions():
    df = pd.read_csv("bigru_predictions.csv")
    return df.to_dict(orient="records")

@app.get("/sentiment")
def get_sentiment():
    df = pd.read_csv("sentiment_scores.csv")
    return df.to_dict(orient="records")

@app.get("/news")
def get_news():
    df = pd.read_csv("news_articles.csv")
    return df[["title", "description", "publishedAt"]].to_dict(orient="records")