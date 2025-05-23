```mermaid
graph TD
    A[backend_python] --> B[app]
    A --> C[instance]
    A --> D[migrations]
    A --> E[README.md]
    A --> F[run.py]

    B --> B1[auth/]
    B --> B2[devices/]
    B --> B3[models/]
    B --> B4[parkinson/]
    B --> B5[users/]
    B --> B6[utils/]
    B --> B7[websocket/]

    B1 --> B1a[__init__.py]
    B1 --> B1b[routes.py]

    B2 --> B2a[__init__.py]
    B2 --> B2b[routes.py]

    B3 --> B3a[__init__.py]
    B3 --> B3b[models.py]

    B4 --> B4a[__init__.py]
    B4 --> B4b[routes.py]

    B5 --> B5a[__init__.py]
    B5 --> B5b[routes.py]

    B6 --> B6a[progress_lstm.py]
    B6 --> B6b[shake_analysis.py]

    B7 --> B7a[__init__.py]
    B7 --> B7b[routes.py]
    B7 --> B7c[server.py]

    C --> C1[app.db]

    D --> D1[alembic.ini]
    D --> D2[env.py]
    D --> D3[README]
    D --> D4[script.py.mako]
    D --> D5[versions/]
