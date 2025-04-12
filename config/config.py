import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    # Application settings
    APP_NAME = "CyberForge OSINT Platform"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    DEBUG = False
    TESTING = False
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Dark web crawler settings
    CRAWLER_INTERVAL = int(os.getenv("CRAWLER_INTERVAL", "3600"))  # Default 1 hour
    MAX_CRAWL_DEPTH = int(os.getenv("MAX_CRAWL_DEPTH", "3"))
    
    # API settings
    API_PREFIX = "/api/v1"
    API_RATE_LIMIT = "100/hour"
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # Monitoring settings
    MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "True") == "True"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")
    

class ProductionConfig(Config):
    """Production configuration."""
    # Production-specific settings
    DEBUG = False
    LOG_LEVEL = "ERROR"
    

# Configuration dictionary
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}

# Get current configuration
def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_by_name[env]