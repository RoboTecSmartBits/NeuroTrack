# Backend Python Application

This application provides Flask-based REST APIs, a WebSocket server, and database models to handle user authentication, device data collection, Parkinson Metric logging, and more. Below is a brief overview of the project structure, key features, and how to use the endpoints externally.

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
   - [app/parkinson/routes.py](app/parkinson/routes.py) logs sensor “shake” data, medication times, and trains or predicts with an LSTM model for daily progression.

5. **WebSocket Server**  
   - [app/websocket/server.py](app/websocket/server.py) starts a WebSocket to receive real-time sensor data.

6. **Database Models**  
   - [app/models/models.py](app/models/models.py) defines database tables (User, Device, SensorData, etc.).

---

## Getting Started

1. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Variables**  
   - Update `.env` with your `SECRET_KEY` and `DATABASE_URI`.
3. **Database Setup**  
   ```bash
   flask db upgrade
   ```
   Or use `/auth/init-db` (for SQLite) to create tables.
4. **Run the Application**  
   ```bash
   python run.py
   ```
   Defaults:  
   - Flask service runs on `http://localhost:5000`  
   - WebSocket server runs on `ws://localhost:8765`

---

## Using the Endpoints Externally

Below are some example commands (using `curl`) to demonstrate how to interact with the endpoints from external code or scripts. Update `localhost:5000` to match your server’s URL.

### 1. Auth

- **Register a new user**  
  ```bash
  curl -X POST -H "Content-Type: application/json" \
       -d '{"email":"user@example.com","password":"mypassword"}' \
       http://localhost:5000/auth/register
  ```
- **Log in (retrieve JWT)**  
  ```bash
  curl -X POST -H "Content-Type: application/json" \
       -d '{"email":"user@example.com","password":"mypassword"}' \
       http://localhost:5000/auth/login
  ```
  Response includes a JWT in `access_token`; pass it as `Authorization: Bearer <token>` for secured endpoints.

### 2. Users

- **Fetch user profile**  
  ```bash
  curl -X GET -H "Authorization: Bearer <token>" \
       http://localhost:5000/users/profile
  ```
- **Update user profile**  
  ```bash
  curl -X PUT -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"name":"New Name","email":"changed@example.com"}' \
       http://localhost:5000/users/profile
  ```

### 3. Devices

- **List all devices**  
  ```bash
  curl -X GET -H "Authorization: Bearer <token>" \
       http://localhost:5000/devices/
  ```
- **Create a new device**  
  ```bash
  curl -X POST -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"name":"MyDevice","description":"Test device"}' \
       http://localhost:5000/devices/
  ```
- **Retrieve device details**  
  ```bash
  curl -X GET -H "Authorization: Bearer <token>" \
       http://localhost:5000/devices/<device_id>
  ```
- **Update a device**  
  ```bash
  curl -X PUT -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"name":"DeviceUpdated"}' \
       http://localhost:5000/devices/<device_id>
  ```
- **Delete a device**  
  ```bash
  curl -X DELETE -H "Authorization: Bearer <token>" \
       http://localhost:5000/devices/<device_id>
  ```
- **Get sensor data for a device**  
  ```bash
  curl -X GET -H "Authorization: Bearer <token>" \
       http://localhost:5000/devices/<device_id>/sensor-data
  ```

### 4. Parkinson

- **Log new shake data**  
  ```bash
  curl -X POST -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"shake_value":123,"timestamp":"2025-05-22T03:00:00Z"}' \
       http://localhost:5000/parkinson/log
  ```
- **Get user shake data by minute**  
  ```bash
  curl -X GET -H "Authorization: Bearer <token>" \
       http://localhost:5000/parkinson/<user_id>/shake-by-minute
  ```
- **Log medication usage time**  
  ```bash
  curl -X POST -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"medication_name":"Carbidopa-Levodopa","timestamp":"2025-05-22T07:00:00Z"}' \
       http://localhost:5000/parkinson/<user_id>/log-medication
  ```
- **Get medication response**  
  ```bash
  curl -X GET -H "Authorization: Bearer <token>" \
       http://localhost:5000/parkinson/<user_id>/medication-response
  ```
- **Train LSTM model**  
  ```bash
  curl -X POST -H "Authorization: Bearer <token>" \
       http://localhost:5000/parkinson/<user_id>/train-progress-lstm
  ```
- **Predict daily progression**  
  ```bash
  curl -X GET -H "Authorization: Bearer <token>" \
       http://localhost:5000/parkinson/<user_id>/predict-progress-lstm
  ```

---

## WebSocket Usage

- **Start the WebSocket server**  
  By default, runs on `ws://localhost:8765`. Send sensor data as JSON or binary frames for real-time processing.  
  Example (JavaScript):
  ```js
  const socket = new WebSocket("ws://localhost:8765");
  socket.onopen = () => {
    socket.send(JSON.stringify({ deviceId: 1, data: [/* values here */] }));
  };
  ```

---

## Contributing

1. **Create a Branch**  
2. **Implement Your Changes**  
3. **Submit a Pull Request**

For questions, check the code comments or open an issue in the repository.