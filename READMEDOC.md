# Backend Python Application

This application provides Flask-based REST APIs, a WebSocket server, and database models to handle user authentication, device data collection, Parkinson Metric logging, and more. Below is a brief overview of the project structure.

---

## Project Structure

```
backend_python/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py              # Handles user registration, login, JWT-based auth
│   ├── devices/
│   │   ├── __init__.py
│   │   └── routes.py              # Devices CRUD, sensor data retrieval, device assignment
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py              # SQLAlchemy models (User, Device, etc.)
│   ├── parkinson/
│   │   ├── __init__.py
│   │   └── routes.py              # Routes to log shake data, medication logs, LSTM training
│   ├── users/
│   │   ├── __init__.py
│   │   └── routes.py              # User profile, update user details
│   ├── utils/
│   │   ├── progress_lstm.py       # LSTM model building & training
│   │   └── shake_analysis.py      # Calculates shake magnitude from sensor data
│   ├── websocket/
│   │   ├── __init__.py
│   │   ├── routes.py              # Receives data via WebSockets, stores device info
│   │   └── server.py              # WebSocket server startup
│   └── __init__.py                # Flask app creation & Blueprint registration
├── migrations/
│   ├── env.py                     # Alembic migration configuration
│   ├── alembic.ini                # Alembic settings
│   ├── script.py.mako             # Alembic migration script template
│   └── README                     # Simple note on single DB config
├── .env                           # Environment variables (e.g., SECRET_KEY, DATABASE_URI)
├── run.py                         # Main entry point to wait for DB and start the Flask app
└── requirements.txt               # (Recommended) Python dependencies for this project
```

---

## Key Features

1. **Authentication and Registration**  
   - Routes in [app/auth/routes.py](app/auth/routes.py) handle user signup, token creation, and login.
   - JSON Web Tokens (JWT) are used for secured endpoints.

2. **User Management**  
   - [app/users/routes.py](app/users/routes.py) offers profile retrieval and updates (name, email, medication details).

3. **Device Management**  
   - [app/devices/routes.py](app/devices/routes.py) allows CRUD operations on devices and retrieving associated sensor data.

4. **Parkinson Metrics**  
   - [app/parkinson/routes.py](app/parkinson/routes.py) logs sensor “shake” data and medication times, and trains or predicts with an LSTM model for daily progression.

5. **WebSocket Server**  
   - [app/websocket/server.py](app/websocket/server.py) starts a WebSocket to receive binary or JSON sensor data in real time.

6. **Database Models**  
   - [app/models/models.py](app/models/models.py) defines tables such as `User`, `Device`, `SensorData`, `ParkinsonMetric`, `MedicationLog`.

---

## Getting Started

1. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Variables**  
   - Update `.env` with your `SECRET_KEY` and `DATABASE_URI`.
3. **Database Setup**  
   - Run migrations (using Alembic/Flask-Migrate) or manually create tables:
     ```bash
     flask db upgrade
     ```
   - Or use `/auth/init-db` route (for SQLite) to quickly create tables.

4. **Run the Application**  
   ```bash
   python run.py
   ```
   - Default port is `5000` for the Flask service, and `8765` for the WebSocket server.

---

## Endpoints Overview

- **Auth**  
  - `POST /auth/register`: Register a new user  
  - `POST /auth/login`: Log in and get a JWT token

- **Users**  
  - `GET /users/profile`: Retrieves a user using JWT auth  
  - `PUT /users/profile`: Updates user fields

- **Devices**  
  - `GET /devices/`: List all devices  
  - `POST /devices/`: Create a new device  
  - `GET /devices/<device_id>`: Retrieve device details  
  - `PUT /devices/<device_id>`: Update an existing device  
  - `DELETE /devices/<device_id>`: Delete a device  
  - `GET /devices/<device_id>/sensor-data`: Retrieve sensor data

- **Parkinson**  
  - `POST /parkinson/log`: Log new shake data  
  - `GET /parkinson/<user_id>/shake-by-minute`: Compute averaged shaking data by minute on a given day  
  - `POST /parkinson/<user_id>/log-medication`: Log medication usage time  
  - `GET /parkinson/<user_id>/medication-response`: Compare pre/post medication shake  
  - `POST /parkinson/<user_id>/train-progress-lstm`: Train LSTM  
  - `GET /parkinson/<user_id>/predict-progress-lstm`: Predict daily progression (`better`/`worse`)

---

## Contributing

1. **Create a Branch**  
2. **Make Your Changes**  
3. **Submit a Pull Request**  

For questions, check out the code comments or open an issue in your repository.
