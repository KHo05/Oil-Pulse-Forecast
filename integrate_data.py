import pandas as pd

# Load data
prices_df = pd.read_csv("oil_prices.csv", index_col=0, parse_dates=True)
lstm_predictions_df = pd.read_csv("lstm_predictions.csv", index_col=0, parse_dates=True)
sentiment_df = pd.read_csv("sentiment_scores.csv", parse_dates=["date"])

# Set date as index for sentiment_df to align with other dataframes
sentiment_df.set_index("date", inplace=True)

# Align all DataFrames to a common date range (intersection of indices)
common_index = prices_df.index.intersection(lstm_predictions_df.index).intersection(sentiment_df.index)
prices_df = prices_df.loc[common_index]
lstm_predictions_df = lstm_predictions_df.loc[common_index]
sentiment_df = sentiment_df.loc[common_index]

# Merge dataframes
integrated_df = prices_df.merge(lstm_predictions_df, left_index=True, right_index=True, how="left")
integrated_df = integrated_df.merge(sentiment_df, left_index=True, right_index=True, how="left")

# Handle missing values
integrated_df["sentiment"] = integrated_df["sentiment"].fillna(0)  # Neutral score for sentiment
integrated_df["Predicted"] = integrated_df["Predicted"].interpolate(method="linear").fillna(method="ffill")  # Interpolate, then forward-fill remaining gaps

# Save integrated data
integrated_df.to_csv("integrated_data.csv")
print("Integrated data saved to integrated_data.csv")