import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("oil_prices.csv", index_col=0, parse_dates=True)
prices = df["4. close"].values.reshape(-1, 1)

# Normalize data
scaler = MinMaxScaler()
prices_scaled = scaler.fit_transform(prices)

# Create sequences (two-week windows)
def create_sequences(data, seq_length=14):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i : i + seq_length])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

X, y = create_sequences(prices_scaled)

# Split data
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Build LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(14, 1)))
model.add(LSTM(50))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")

# Train model
model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.1)

# Predict
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)
y_test = scaler.inverse_transform(y_test)

# Save predictions
results = pd.DataFrame({"Actual": y_test.flatten(), "Predicted": predictions.flatten()}, index=df.index[-len(y_test):])
results.to_csv("lstm_predictions.csv")

# Plot
plt.plot(results.index, results["Actual"], label="Actual")
plt.plot(results.index, results["Predicted"], label="Predicted")
plt.xlabel("Date")
plt.ylabel("Price")
plt.title("LSTM Predictions vs Actual Oil Prices (OILK)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()