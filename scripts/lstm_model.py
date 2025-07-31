import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import os

# Define the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "oil-pulse-forecast-backend", "data")

# Load data
df = pd.read_csv(os.path.join(DATA_DIR, "oil_prices.csv"), index_col=0, parse_dates=True)
prices = df["4. close"].values.reshape(-1, 1)

# Normalize data
scaler = MinMaxScaler()
prices_scaled = scaler.fit_transform(prices)

# Create sequences
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

# Build LSTM model with dropout
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(14, 1)))
model.add(Dropout(0.2))
model.add(LSTM(50))
model.add(Dropout(0.2))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")

# Train model with early stopping
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.1, callbacks=[early_stop])

# Predict on test set
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)
y_test = scaler.inverse_transform(y_test)

# Evaluate
mae = mean_absolute_error(y_test, predictions)
print(f"Test MAE: {mae}")

# Predict on entire dataset for integration
all_predictions = model.predict(X)
all_predictions = scaler.inverse_transform(all_predictions)
y_actual = scaler.inverse_transform(y)
results_all = pd.DataFrame({"Actual": y_actual.flatten(), "Predicted": all_predictions.flatten()}, index=df.index[14:])
results_all.rename_axis("date").to_csv(os.path.join(DATA_DIR, "lstm_predictions.csv"))

# Plot test results
results_test = pd.DataFrame({"Actual": y_test.flatten(), "Predicted": predictions.flatten()}, index=df.index[-len(y_test):])
plt.plot(results_test.index, results_test["Actual"], label="Actual")
plt.plot(results_test.index, results_test["Predicted"], label="Predicted")
plt.xlabel("Date")
plt.ylabel("Price")
plt.title("LSTM Predictions vs Actual Oil Prices (OILK)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()