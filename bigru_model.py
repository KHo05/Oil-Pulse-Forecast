import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Bidirectional, GRU, Dense
import matplotlib.pyplot as plt

# Load integrated data
df = pd.read_csv("integrated_data.csv", index_col=0, parse_dates=True)
data = df[["4. close", "Predicted", "sentiment"]].values

# Normalize data
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

# Create sequences
def create_sequences(data, seq_length=14):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i : i + seq_length])
        y.append(data[i + seq_length, 0])  # Predict closing price
    return np.array(X), np.array(y)

X, y = create_sequences(data_scaled)

# Split data
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Build BiGRU model
model = Sequential()
model.add(Bidirectional(GRU(50, return_sequences=True), input_shape=(14, 3)))
model.add(Bidirectional(GRU(50)))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")

# Train model
model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.1)

# # Predict
# predictions = model.predict(X_test)
# predictions = scaler.inverse_transform(np.hstack((predictions, np.zeros((predictions.shape[0], 2)))))
# y_test = scaler.inverse_transform(np.hstack((y_test.reshape(-1, 1), np.zeros((y_test.shape[0], 2)))))

# # Save predictions
# results = pd.DataFrame({"Actual": y_test[:, 0], "Predicted": predictions[:, 0]})
# results.to_csv("bigru_predictions.csv")

# # Plot
# plt.plot(results["Actual"], 'o', label="Actual")  # Circle marker
# plt.plot(results["Predicted"], 'x', label="Predicted")  # X marker
# plt.legend()
# plt.show()

# After training
all_predictions = model.predict(X)
all_predictions = scaler.inverse_transform(np.hstack((all_predictions, np.zeros((all_predictions.shape[0], 2)))))
y_actual = scaler.inverse_transform(np.hstack((y.reshape(-1, 1), np.zeros((y.shape[0], 2)))))
results_all = pd.DataFrame({"Actual": y_actual[:, 0], "Predicted": all_predictions[:, 0]}, index=df.index[14:])
plt.plot(results_all["Actual"], label="Actual")
plt.plot(results_all["Predicted"], label="Predicted")
plt.legend()
plt.show()