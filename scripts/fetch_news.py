import requests
import pandas as pd
import time
import os

# Define the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "oil-pulse-forecast-backend", "data")

API_KEY = "98747665b0fc45e4b293c6fdfda14180"  # Replace with your key
query = "oil prices"
FROM_DATE = "2021-07-29"
TO_DATE = "2025-07-29"
url = f"https://newsapi.org/v2/everything?q={query}&from={FROM_DATE}&to={TO_DATE}&apiKey={API_KEY}"
MAX_RETRIES = 3

for attempt in range(MAX_RETRIES):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()  

        if data["status"] != "ok":
            print(f"API Error: {data.get('message', 'Unknown error')}")
            exit()

        # Extract articles
        articles = data["articles"]
        df = pd.DataFrame(articles)
        df = df[["publishedAt", "title", "description"]]  # Keep only relevant columns

        # Save to CSV
        df.to_csv(os.path.join(DATA_DIR, "news_articles.csv"), index=False)
        print(f"News fetched and saved to {os.path.join(DATA_DIR, 'news_articles.csv')}")
        break

    except (requests.RequestException, ValueError) as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(5)
        else:
            print("Max retries reached. Exiting.")
            exit()