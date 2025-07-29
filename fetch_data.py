import requests
import pandas as pd

API_KEY = "S8T54DZ7NA1DLK7I"  # Replace with your valid Alpha Vantage API key
symbol = "OILK"  # ProShares K-1 Free Crude Oil Strategy ETF
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}"

response = requests.get(url)
data = response.json()

# Check for errors in the API response
if "Error Message" in data:
    print(f"API Error: {data['Error Message']}")
    exit()
elif "Information" in data:
    print(f"API Info: {data['Information']}")
    exit()
elif "Time Series (Daily)" not in data:
    print("Unexpected response format:", data)
    exit()

# Extract time series data
time_series = data["Time Series (Daily)"]
df = pd.DataFrame.from_dict(time_series, orient="index")
df = df.astype(float)
df.index = pd.to_datetime(df.index)
df = df.sort_index()

# Filter for the desired date range (4 years)
df = df["2021-07-29":"2025-07-29"]

# Save to CSV
df.to_csv("oil_prices.csv")
print("Data fetched and saved to oil_prices.csv")