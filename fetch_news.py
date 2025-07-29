import requests
import pandas as pd

API_KEY = "98747665b0fc45e4b293c6fdfda14180"  # Replace with your key
query = "oil prices"
url = f"https://newsapi.org/v2/everything?q={query}&apiKey={API_KEY}"

response = requests.get(url)
data = response.json()

# Extract articles
articles = data["articles"]
df = pd.DataFrame(articles)

# Save to CSV
df.to_csv("news_articles.csv")
print("News fetched and saved to news_articles.csv")