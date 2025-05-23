import os
import numpy as np
import pandas as pd
from datetime import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

from app.models.models import ParkinsonMetric

# Directory for saving models
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def build_lstm_data(user_id, timesteps=3):
    """
    Build sequences of daily shake averages for LSTM input.
    Each sample: [shake_{t-3}, shake_{t-2}, shake_{t-1}], 
    label: better(1)/worse(0) at t
    """
    qs = ParkinsonMetric.query.filter_by(user_id=user_id) \
                              .order_by(ParkinsonMetric.timestamp).all()
    if len(qs) < timesteps + 1:
        return None, None

    # Compute daily average shake
    df = pd.DataFrame([{'date': m.timestamp.date(), 'shake': m.shake_per_minute}
                       for m in qs])
    daily = df.groupby('date').shake.mean().sort_index().reset_index()
    shakes = daily.shake.values

    X, y = [], []
    for i in range(timesteps, len(shakes)):
        seq = shakes[i - timesteps:i]
        label = 1 if shakes[i] < shakes[i-1] else 0
        X.append(seq)
        y.append(label)

    X = np.array(X).reshape(-1, timesteps, 1)
    y = np.array(y)
    return X, y

def train_lstm_model(user_id, timesteps=3, epochs=50, batch_size=8):
    """
    Trains LSTM on the user's daily shake sequences.
    Saves to MODEL_DIR as 'progress_lstm_{user_id}.h5'.
    """
    X, y = build_lstm_data(user_id, timesteps)
    if X is None:
        raise ValueError("Not enough data for LSTM training")

    model = Sequential([
        LSTM(32, input_shape=(timesteps, 1)),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    es = EarlyStopping(patience=5, restore_best_weights=True)
    model.fit(X, y, epochs=epochs, batch_size=batch_size, callbacks=[es], verbose=1)

    path = os.path.join(MODEL_DIR, f'progress_lstm_{user_id}.h5')
    model.save(path)
    return path
