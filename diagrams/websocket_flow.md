```mermaid
sequenceDiagram
    participant Client
    participant WebSocketServer
    participant FlaskApp
    participant Database

    Client->>WebSocketServer: Connect
    WebSocketServer->>FlaskApp: Register Device
    FlaskApp->>Database: Add Device Entry
    Database-->>FlaskApp: Success
    FlaskApp-->>WebSocketServer: Device Registered
    WebSocketServer-->>Client: Connection Established

    Client->>WebSocketServer: Send Sensor Data
    WebSocketServer->>FlaskApp: Process Data
    FlaskApp->>Database: Store Sensor Data
    Database-->>FlaskApp: Success
    FlaskApp-->>WebSocketServer: Data Stored
