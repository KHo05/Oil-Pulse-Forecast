from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os

# Define the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "oil-pulse-forecast-backend", "data")

analyzer = SentimentIntensityAnalyzer()

# Load news articles
df = pd.read_csv(os.path.join(DATA_DIR, "news_articles.csv"))

# Combine title and description for sentiment analysis
df["text"] = df["title"].fillna("") + " " + df["description"].fillna("")

# Enhanced sentiment analysis with weighting
def weighted_sentiment(text):
    scores = analyzer.polarity_scores(text)
    # Weight compound score by magnitude of sentiment
    return scores['compound'] * (abs(scores['compound']) ** 0.5)

df["sentiment"] = df["text"].apply(weighted_sentiment)

# Group by date and compute weighted average sentiment
df["date"] = pd.to_datetime(df["publishedAt"]).dt.date
sentiment_df = df.groupby("date")["sentiment"].mean().reset_index()

# Normalize sentiment scores to [-0.5, 0.5] range
scaler = MinMaxScaler(feature_range=(-0.5, 0.5))
sentiment_df["sentiment"] = scaler.fit_transform(sentiment_df[["sentiment"]])

# Save to CSV
sentiment_df.to_csv(os.path.join(DATA_DIR, "sentiment_scores.csv"), index=False)
print(f"Enhanced sentiment scores saved to {os.path.join(DATA_DIR, 'sentiment_scores.csv')}")