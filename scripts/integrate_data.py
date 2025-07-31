import pandas as pd
import os

# Define the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "oil-pulse-forecast-backend", "data")

# Load the datasets
prices_df = pd.read_csv(os.path.join(DATA_DIR, "oil_prices.csv"), index_col=0, parse_dates=True)
lstm_predictions_df = pd.read_csv(os.path.join(DATA_DIR, "lstm_predictions.csv"), index_col=0, parse_dates=True)

## Ensemble approach
# Align dates with LSTM sequence
start_date = prices_df.index.min() + pd.Timedelta(days=14)
prices_df = prices_df[start_date:]

# Merge ONLY price data and LSTM predictions
integrated_df = prices_df.merge(
    lstm_predictions_df[["Predicted"]],
    left_index=True,
    right_index=True,
    how="left"
)

# Fill missing predictions
integrated_df["Predicted"] = integrated_df["Predicted"].ffill().bfill()

# Save (without sentiment)
integrated_df.to_csv(os.path.join(DATA_DIR, "integrated_data.csv"))
print(f"Integrated data saved to {os.path.join(DATA_DIR, 'integrated_data.csv')}")

## SENTIMENT ANALYSIS APPROACH
# sentiment_df = pd.read_csv(os.path.join(DATA_DIR, "sentiment_scores.csv"), parse_dates=["date"])

# # Set the date column as the index for sentiment data
# sentiment_df.set_index("date", inplace=True)

# # Skip the first 14 days from prices_df to align with LSTM sequence length
# start_date = prices_df.index.min() + pd.Timedelta(days=20)
# prices_df = prices_df[start_date:]

# # Merge datasets, keeping all dates from the filtered price data
# integrated_df = prices_df.merge(lstm_predictions_df, left_index=True, right_index=True, how="left")
# integrated_df = integrated_df.merge(sentiment_df, left_index=True, right_index=True, how="left")

# # Fill missing sentiment scores with 0 (neutral sentiment)
# integrated_df["sentiment"] = integrated_df["sentiment"].fillna(0)

# # Fill missing LSTM predictions: forward-fill, then back-fill if needed
# integrated_df["Predicted"] = integrated_df["Predicted"].fillna(method="ffill")
# integrated_df["Predicted"] = integrated_df["Predicted"].fillna(method="bfill")

# # Save the updated file
# integrated_df.to_csv(os.path.join(DATA_DIR, "integrated_data.csv"))
# print(f"Integrated data saved to {os.path.join(DATA_DIR, 'integrated_data.csv')}")