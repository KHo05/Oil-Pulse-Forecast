import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Bidirectional, GRU, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import os

# Define the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "oil-pulse-forecast-backend", "data")

## Ensemble approach
# Load integrated data
df = pd.read_csv(os.path.join(DATA_DIR, "integrated_data.csv"), index_col=0, parse_dates=True)

# Use ONLY historical prices and LSTM predictions (REMOVE SENTIMENT)
data = df[["4. close", "Predicted"]].values

# Normalize features and target separately
scaler_features = MinMaxScaler()
scaler_target = MinMaxScaler()
data_scaled = scaler_features.fit_transform(data)
y_scaled = scaler_target.fit_transform(data[:, 0].reshape(-1, 1))

# Create sequences
def create_sequences(data, y, seq_length=14):
    X, y_seq = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i : i + seq_length])
        y_seq.append(y[i + seq_length])
    return np.array(X), np.array(y_seq)

X, y = create_sequences(data_scaled, y_scaled)

# Split data
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Build BiGRU model with dropout (reduced complexity)
model = Sequential()
model.add(Bidirectional(GRU(32, return_sequences=True), input_shape=(14, 2)))  # Input shape changed to 2 features
model.add(Dropout(0.2))
model.add(Bidirectional(GRU(32)))
model.add(Dropout(0.2))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")

# Train model with early stopping
early_stop = EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True)
history = model.fit(
    X_train, y_train, 
    epochs=50, 
    batch_size=16, 
    validation_split=0.15, 
    callbacks=[early_stop],
    verbose=1
)

# Predict on test set
predictions = model.predict(X_test)
predictions = scaler_target.inverse_transform(predictions)
y_test = scaler_target.inverse_transform(y_test)

# Evaluate
mae = mean_absolute_error(y_test, predictions)
print(f"Test MAE: {mae}")

# Ensemble prediction: Weighted average of BiGRU and LSTM
all_predictions = model.predict(X)
all_predictions = scaler_target.inverse_transform(all_predictions)
lstm_predictions = df["Predicted"].values[14:].reshape(-1, 1)

# Weighted ensemble (70% BiGRU, 30% LSTM)
ensemble_predictions = 0.7 * all_predictions + 0.3 * lstm_predictions

y_actual = scaler_target.inverse_transform(y)
results_all = pd.DataFrame({
    "Actual": y_actual.flatten(), 
    "Predicted": ensemble_predictions.flatten()
}, index=df.index[14:])
results_all.rename_axis("date").to_csv(os.path.join(DATA_DIR, "bigru_predictions.csv"))

# Plot
plt.figure(figsize=(12, 6))
plt.plot(results_all.index, results_all["Actual"], label="Actual", linewidth=2)
plt.plot(results_all.index, results_all["Predicted"], label="Predicted", linestyle='--')
plt.xlabel("Date")
plt.ylabel("Price")
plt.title("Ensemble Predictions vs Actual Oil Prices")
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("bigru_predictions_plot.png", dpi=300)
plt.show()

## SENTIMENT ANALYSIS APPROACH
# # Load integrated data
# df = pd.read_csv(os.path.join(DATA_DIR, "integrated_data.csv"), index_col=0, parse_dates=True)
# data = df[["4. close", "Predicted", "sentiment"]].values

# # Normalize features and target separately
# scaler_features = MinMaxScaler()
# scaler_target = MinMaxScaler()
# data_scaled = scaler_features.fit_transform(data)
# y_scaled = scaler_target.fit_transform(data[:, 0].reshape(-1, 1))

# # Create sequences
# def create_sequences(data, y, seq_length=14):
#     X, y_seq = [], []
#     for i in range(len(data) - seq_length):
#         X.append(data[i : i + seq_length])
#         y_seq.append(y[i + seq_length])
#     return np.array(X), np.array(y_seq)

# X, y = create_sequences(data_scaled, y_scaled)

# # Split data
# train_size = int(len(X) * 0.8)
# X_train, X_test = X[:train_size], X[train_size:]
# y_train, y_test = y[:train_size], y[train_size:]

# # Build BiGRU model with dropout
# model = Sequential()
# model.add(Bidirectional(GRU(50, return_sequences=True), input_shape=(14, 3)))
# model.add(Dropout(0.2))
# model.add(Bidirectional(GRU(50)))
# model.add(Dropout(0.2))
# model.add(Dense(1))
# model.compile(optimizer="adam", loss="mse")

# # Train model with early stopping
# early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
# model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.1, callbacks=[early_stop])

# # Predict on test set
# predictions = model.predict(X_test)
# predictions = scaler_target.inverse_transform(predictions)
# y_test = scaler_target.inverse_transform(y_test)

# # Evaluate
# mae = mean_absolute_error(y_test, predictions)
# print(f"Test MAE: {mae}")

# # Predict on entire dataset
# all_predictions = model.predict(X)
# all_predictions = scaler_target.inverse_transform(all_predictions)
# y_actual = scaler_target.inverse_transform(y)
# results_all = pd.DataFrame({"Actual": y_actual.flatten(), "Predicted": all_predictions.flatten()}, index=df.index[14:])
# results_all.to_csv(os.path.join(DATA_DIR, "bigru_predictions.csv"))

# # Plot
# plt.plot(results_all.index, results_all["Actual"], label="Actual")
# plt.plot(results_all.index, results_all["Predicted"], label="Predicted", linestyle='--')
# plt.xlabel("Date")
# plt.ylabel("Price")
# plt.title("BiGRU Predictions vs Actual Oil Prices")
# plt.legend()
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()