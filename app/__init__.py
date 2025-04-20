"""
Autonomous Shipping Truck Management Platform - Application Package
"""
from flask import Flask
from flask_cors import CORS
from config.config import config_by_name

def create_app(config_name='development'):
    """
    Create and configure the Flask application
    
    Args:
        config_name (str): Configuration environment to use
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    app.config.from_object(config_by_name[config_name])
    
    # Set secret key for sessions
    app.secret_key = app.config.get('SECRET_KEY', 'autonomous-shipping-truck-secret-key')
    
    # Configure session settings
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
    
    # Register blueprints
    from app.routes import main_blueprint, api_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # AWS Services initialization
    from app.utils.aws_utils import init_aws_services
    init_aws_services(app)
    
    return app
