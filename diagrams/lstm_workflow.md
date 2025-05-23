```mermaid
flowchart TD
    A[build_lstm_data()] --> B[Query ParkinsonMetric]
    B --> C[Compute Daily Shake Averages]
    C --> D[Build Sequences for LSTM]
    D --> E[train_lstm_model()]
    E --> F[Initialize LSTM Model]
    F --> G[Train Model with Data]
    G --> H[Save Trained Model]
    H --> I[predict_progress_lstm()]
    I --> J[Load Trained Model]
    J --> K[Make Predictions]
