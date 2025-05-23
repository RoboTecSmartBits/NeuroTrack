```mermaid
erDiagram
    USER {
        string id PK
        string nume
        int age
        string password
        string emails
        string medicamente
    }
    DEVICE {
        string id PK
        string name
        string user_id FK
    }
    SENSORDATA {
        string id PK
        string device_id FK
        datetime timestamp
        float value
    }
    PARKINSONMETRIC {
        string id PK
        string user_id FK
        datetime timestamp
        float shake_per_minute
    }
    MEDICATIONLOG {
        string id PK
        string user_id FK
        datetime timestamp
        string medication
    }

    USER ||--o{ DEVICE : "has"
    USER ||--o{ PARKINSONMETRIC : "has"
    USER ||--o{ MEDICATIONLOG : "has"
    DEVICE ||--o{ SENSORDATA : "has"
