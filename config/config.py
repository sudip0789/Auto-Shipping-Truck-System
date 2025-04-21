"""
Configuration module for different environments
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key-for-dev'
    DEBUG = False
    TESTING = False
    
    # AWS Settings
    AWS_REGION = 'us-east-2'
    AWS_ACCESS_KEY = 'AKIAQQABDUVERYN7SE7B'
    AWS_SECRET_KEY = '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'
    
    # DynamoDB table names
    DYNAMODB_USERS_TABLE = 'ast-users'
    DYNAMODB_TRUCKS_TABLE = 'ast-trucks'
    DYNAMODB_ALERTS_TABLE = 'ast-alerts'
    DYNAMODB_ROUTES_TABLE = 'ast-routes'
    DYNAMODB_DETECTIONS_TABLE = 'ast-detections'
    
    # S3 Bucket names
    S3_BUCKET_NAME = 'ast-data-bucket'
    
    # CARLA Simulation settings
    CARLA_SERVER = os.environ.get('CARLA_SERVER') or 'localhost'
    CARLA_PORT = os.environ.get('CARLA_PORT') or 2000


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    
    
class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    
    # In production, all secrets should be properly set in environment variables
    def __init__(self):
        if not all([
            os.environ.get('SECRET_KEY'),
            os.environ.get('AWS_ACCESS_KEY'),
            os.environ.get('AWS_SECRET_KEY')
        ]):
            raise ValueError("Production environment requires all secrets to be set")


# Config dictionary to map environment names to config classes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
