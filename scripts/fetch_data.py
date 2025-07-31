import requests
import pandas as pd
import time
import os

# Define the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "oil-pulse-forecast-backend", "data")

API_KEY = "S8T54DZ7NA1DLK7I"  # Replace with your valid Alpha Vantage API key
symbol = "OILK"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}"

# Configurable date range
START_DATE = "2021-07-29"
END_DATE = "2025-07-29"
MAX_RETRIES = 3

for attempt in range(MAX_RETRIES):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check for API errors
        if "Error Message" in data:
            print(f"API Error: {data['Error Message']}")
            exit()
        elif "Information" in data:
            print(f"API Info: {data['Information']}")
            exit()
        elif "Time Series (Daily)" not in data:
            print("Unexpected response format:", data)
            exit()

        # Extract and process data
        time_series = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df[START_DATE:END_DATE]

        # Save to CSV
        df.rename_axis("date").to_csv(os.path.join(DATA_DIR, "oil_prices.csv"))
        print(f"Data fetched and saved to {os.path.join(DATA_DIR, 'oil_prices.csv')}")
        break

    except (requests.RequestException, ValueError) as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(5)  # Wait before retrying
        else:
            print("Max retries reached. Exiting.")
            exit()