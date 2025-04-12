Installation
============

Prerequisites
------------

* Python 3.9 or higher
* PostgreSQL 12 or higher
* Redis 6 or higher
* Tor (optional, for dark web access)

Installation from Source
-----------------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/your-org/cyberforge.git
      cd cyberforge

2. Create and activate a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

4. Configure environment variables:

   Create a `.env` file in the project root with the following variables:

   .. code-block:: bash

      # Database
      DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cyberforge

      # Redis
      REDIS_URL=redis://localhost:6379/0

      # Secret keys
      SECRET_KEY=your-secret-key
      JWT_SECRET_KEY=your-jwt-secret-key

      # Tor proxy (optional)
      TOR_PROXY_HOST=localhost
      TOR_PROXY_PORT=9050

      # Logging
      LOG_LEVEL=INFO

5. Run database migrations:

   .. code-block:: bash

      alembic upgrade head

Docker Installation
------------------

1. Build and run with docker-compose:

   .. code-block:: bash

      docker-compose up -d

   This will start the following services:
   
   * CyberForge API
   * PostgreSQL database
   * Redis
   * Celery worker
   * Tor proxy (optional)

2. Access the API at http://localhost:8000

Environment Variables
--------------------

The application is configured using environment variables or a `.env` file.

Required Variables:

* ``DATABASE_URL`` - PostgreSQL connection string
* ``SECRET_KEY`` - Secret key for session encryption
* ``JWT_SECRET_KEY`` - Secret key for JWT token encryption

Optional Variables:

* ``FLASK_ENV`` - Environment (development, test, or production)
* ``LOG_LEVEL`` - Logging level (DEBUG, INFO, WARNING, ERROR)
* ``TOR_PROXY_HOST`` - Tor proxy hostname or IP
* ``TOR_PROXY_PORT`` - Tor proxy port
* ``REDIS_URL`` - Redis connection string
* ``CRAWLER_INTERVAL`` - Interval for crawler jobs in seconds
* ``MAX_CRAWL_DEPTH`` - Maximum depth for web crawling