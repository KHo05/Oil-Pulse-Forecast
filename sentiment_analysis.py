from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

analyzer = SentimentIntensityAnalyzer()
# Load news articles
df = pd.read_csv("news_articles.csv")

# Compute sentiment scores
df["sentiment"] = df["description"].apply(lambda x: analyzer.polarity_scores(str(x))["compound"])

# Group by date and compute average sentiment
df["date"] = pd.to_datetime(df["publishedAt"]).dt.date
sentiment_df = df.groupby("date")["sentiment"].mean().reset_index()

# Save to CSV
sentiment_df.to_csv("sentiment_scores.csv")
print("Sentiment scores saved to sentiment_scores.csv")