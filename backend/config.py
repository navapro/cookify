import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Make sure we're loading from the correct directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    # Database configuration
    # read from .env file
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Judy@2004')
    MYSQL_DB = os.getenv('MYSQL_DB', 'cookify')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

    # URL encode the password to handle special characters
    encoded_password = quote_plus(MYSQL_PASSWORD)

    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = f'mysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
