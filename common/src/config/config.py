import os
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Config:
    """Configuration manager for CARIS system"""
    
    # Database configurations
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://caris_user:caris_password@localhost:5432/caris_db')
    MYSQL_URL = os.getenv('MYSQL_URL', 'mysql://caris_user:caris_password@localhost:3306/caris_db')
    MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
    
    # API configurations
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Data paths
    RAW_DATA_PATH = os.getenv('RAW_DATA_PATH', './data/raw')
    PROCESSED_DATA_PATH = os.getenv('PROCESSED_DATA_PATH', './data/processed')
    REPORT_PATH = os.getenv('REPORT_PATH', './reporting-service/reports')
    
    # Model paths
    CHURN_MODEL_PATH = os.getenv('CHURN_MODEL_PATH', './models/churn_model.pkl')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')
    
    # Email
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 60))  # seconds
    
    @classmethod
    def get_database_url(cls, db_type='postgresql'):
        """Get database URL for specific database type"""
        if db_type == 'postgresql':
            return cls.DATABASE_URL
        elif db_type == 'mysql':
            return cls.MYSQL_URL
        elif db_type == 'mongodb':
            return cls.MONGODB_URL
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        required_vars = ['SECRET_KEY']
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            logger.warning(f"Missing configuration variables: {missing}")
        return len(missing) == 0

# Export configuration
config = Config()
DATABASE_URL = config.DATABASE_URL
API_HOST = config.API_HOST
API_PORT = config.API_PORT
SECRET_KEY = config.SECRET_KEY