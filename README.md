# CyberForge Dashboard

A comprehensive dark web intelligence platform for monitoring, analyzing, and visualizing potential threats and data breaches.

## Features

### Core Functionality
- Dark web content monitoring and scraping
- Threat intelligence dashboard with visualization
- Indicator of compromise (IOC) tracking
- Alerting system for detected threats
- Reporting and analytics

### Enhanced Security Features
- **OSINT Integration:** Correlates dark web data with intelligence from VirusTotal and AlienVault OTX
- **API Security:** JWT tokens, API keys, rate limiting, and role-based access controls
- **Data Privacy:** PII detection and masking to protect sensitive information

## Technical Stack

- **Backend:** FastAPI, SQLAlchemy, Async PostgreSQL
- **Frontend:** Streamlit
- **Database:** PostgreSQL
- **Integration:** Support for external OSINT feeds and Tor proxying
- **Security:** JWT authentication, API key management, data masking

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cyberforge-dashboard.git
cd cyberforge-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements_hf.txt
```

3. Set up environment variables:
```
DATABASE_URL=postgresql://user:password@localhost/cyberforge
JWT_SECRET_KEY=your_secret_key
```

4. Run the application:
```bash
streamlit run app.py
```

## API Documentation

The API provides endpoints for:
- Authentication and user management
- Threat intelligence submission and retrieval
- Dark web content scraping and analysis
- Alerts and notifications

API documentation is available at `/docs` when running the API server.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ by [Your Name/Organization]