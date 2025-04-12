Architecture
============

System Architecture
------------------

CyberForge follows a modern, service-oriented architecture with the following components:

.. code-block:: text

    ┌────────────┐     ┌────────────┐     ┌────────────┐
    │            │     │            │     │            │
    │  Frontend  │────▶│  REST API  │────▶│  Database  │
    │            │     │            │     │            │
    └────────────┘     └────────────┘     └────────────┘
           │                 │                  ▲
           │                 │                  │
           │                 ▼                  │
           │          ┌────────────┐           │
           │          │            │           │
           └─────────▶│   Celery   │───────────┘
                      │  Workers   │
                      │            │
                      └────────────┘
                            │
                            ▼
                     ┌────────────┐
                     │            │
                     │ Tor Proxy  │
                     │            │
                     └────────────┘
                            │
                            ▼
                      ┌──────────┐
                      │          │
                      │ Dark Web │
                      │          │
                      └──────────┘

* **Frontend**: Streamlit-based web application for user interaction
* **REST API**: FastAPI application providing all backend functionality
* **Database**: PostgreSQL database for storing threats, indicators, etc.
* **Celery Workers**: Background workers for scheduled tasks and long-running operations
* **Tor Proxy**: Proxy for accessing .onion sites on the dark web

Technology Stack
---------------

Backend:
~~~~~~~~

* **FastAPI**: Modern, fast API framework with automatic OpenAPI docs
* **SQLAlchemy**: SQL toolkit and ORM for database interaction
* **Asyncpg**: Asynchronous PostgreSQL driver
* **Celery**: Distributed task queue
* **Redis**: Message broker and result backend for Celery
* **Alembic**: Database migration tool
* **PyJWT**: JWT token handling for authentication
* **Trafilatura**: Web scraping library
* **PySocks**: SOCKS proxy client for Tor
* **Pandas**: Data manipulation and analysis

Frontend:
~~~~~~~~~

* **Streamlit**: Data application framework
* **Plotly**: Interactive visualization library
* **Pandas**: Data manipulation and analysis

Database Schema
--------------

.. code-block:: text

    ┌─────────┐     ┌─────────┐     ┌──────────┐
    │  User   │     │ Threat  │     │ Indicator│
    ├─────────┤     ├─────────┤     ├──────────┤
    │ id      │     │ id      │     │ id       │
    │ username│     │ title   │     │ value    │
    │ email   │◄────┤ user_id │     │ type     │
    │ password│     │ severity│◄────┤ threat_id│
    │ role    │     │ status  │     │ verified │
    └─────────┘     │ category│     └──────────┘
                    │ source  │
                    └─────────┘
                         │
                         │     ┌─────────┐
                         │     │ Alert   │
                         │     ├─────────┤
                         │     │ id      │
                         └────▶│threat_id│
                               │ user_id │
                               │ created │
                               │ read    │
                               └─────────┘

* **User**: User accounts with authentication and role information
* **Threat**: Potential threats identified from dark web or other sources
* **Indicator**: Indicators of compromise associated with threats
* **Alert**: Notifications for users about relevant threats

Authentication
-------------

The system uses JWT (JSON Web Tokens) for authentication. The typical flow is:

1. User logs in with username and password
2. Server validates credentials and issues a JWT token
3. Client includes the token in the Authorization header for subsequent requests
4. Server validates the token for protected endpoints

Background Tasks
---------------

Scheduled tasks are handled by Celery workers:

* Dark web scanning: Periodically scan specified dark web sources
* Threat intelligence updates: Update information about existing threats
* Alert generation: Create alerts for users based on new threats
* Data cleanup: Remove old data and maintain database performance