import os
import time
import pymysql
import logging
import json
from datetime import datetime
from flask import Flask, request
from models import *
from sqlalchemy.exc import OperationalError
from flask_cors import CORS


# Configure structured logging
class StructuredLogger:
    def __init__(self, service_name="chatapp"):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        
        # Configure JSON formatter for structured logs
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log(self, level, message, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "service": self.service_name,
            "message": message,
            **kwargs
        }
        
        # Add request context if available
        try:
            from flask import has_request_context, request
            if has_request_context():
                log_entry.update({
                    "request_id": request.headers.get('X-Request-ID', 'unknown'),
                    "method": request.method,
                    "endpoint": request.endpoint,
                    "remote_addr": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent', 'unknown')
                })
        except:
            pass
        
        if level == "ERROR":
            self.logger.error(json.dumps(log_entry))
        elif level == "WARNING":
            self.logger.warning(json.dumps(log_entry))
        elif level == "DEBUG":
            self.logger.debug(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))
    
    def info(self, message, **kwargs):
        self.log("INFO", message, **kwargs)
    
    def error(self, message, **kwargs):
        self.log("ERROR", message, **kwargs)
    
    def warning(self, message, **kwargs):
        self.log("WARNING", message, **kwargs)
    
    def debug(self, message, **kwargs):
        self.log("DEBUG", message, **kwargs)


class MockLogger:
    """Mock logger for tests that don't need structured logging"""
    def info(self, message, **kwargs):
        pass
    
    def error(self, message, **kwargs):
        pass
    
    def warning(self, message, **kwargs):
        pass
    
    def debug(self, message, **kwargs):
        pass
    
    def log(self, level, message, **kwargs):
        pass


def create_app():
    pymysql.install_as_MySQLdb()
    app = Flask(__name__)
    
    # Initialize structured logger only if not in testing mode
    if app.config.get('TESTING', False):
        # Override Flask's default logger with our mock
        app.logger = MockLogger()
        # Also set it as a property for direct access
        setattr(app, 'logger', MockLogger())
    else:
        app.logger = StructuredLogger("chatapp")
    
    CORS(
        app,
        origins=["https://dvfx7k0839335.cloudfront.net"],
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type"]
    )

    MYSQL_URI = os.getenv('MYSQL_URI', 'MYSQL uri not set')
    db_uri = f'mysql+pymysql://{MYSQL_URI}' 

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    db.init_app(app)

    # Initialize Prometheus metrics only if not in testing mode
    if not app.config.get('TESTING', False):
        try:
            from prometheus_flask_exporter import PrometheusMetrics
            metrics = PrometheusMetrics(app)
            
            # Add custom application info
            metrics.info('chatapp_info', 'ChatApp application info', version='1.0.0')
            
            # Custom metrics
            from prometheus_client import Counter, Gauge, Histogram
            
            # Counters (always increasing)
            messages_sent = Counter('chatapp_messages_total', 'Total messages sent', ['room'])
            username_changes = Counter('chatapp_username_changes_total', 'Total username changes')
            chat_clears = Counter('chatapp_chat_clears_total', 'Total chat clears', ['room'])
            
            # Gauges (can go up and down)
            active_rooms = Gauge('chatapp_active_rooms', 'Number of active rooms')
            total_users = Gauge('chatapp_total_users', 'Total number of users')
            database_connection = Gauge('chatapp_database_connected', 'Database connection status (1=connected, 0=disconnected)')
            messages_today = Gauge('chatapp_messages_today', 'Messages sent today')
            
            # Histograms (for measuring distributions)
            message_length = Histogram('chatapp_message_length_chars', 'Distribution of message lengths', buckets=[10, 50, 100, 200, 500, 1000])
            
            # Store metrics in app context for use in routes
            app.metrics = {
                'messages_sent': messages_sent,
                'username_changes': username_changes,
                'chat_clears': chat_clears,
                'active_rooms': active_rooms,
                'total_users': total_users,
                'database_connection': database_connection,
                'messages_today': messages_today,
                'message_length': message_length
            }
        except ImportError:
            # If prometheus_flask_exporter is not available, use mock metrics
            class MockMetrics:
                def __init__(self):
                    pass
                def labels(self, **kwargs):
                    return self
                def inc(self):
                    pass
                def set(self, value):
                    pass
                def observe(self, value):
                    pass
            
            app.metrics = {
                'messages_sent': MockMetrics(),
                'username_changes': MockMetrics(),
                'chat_clears': MockMetrics(),
                'active_rooms': MockMetrics(),
                'total_users': MockMetrics(),
                'database_connection': MockMetrics(),
                'messages_today': MockMetrics(),
                'message_length': MockMetrics()
            }

    # Log app startup only if not testing
    if not app.config.get('TESTING', False):
        app.logger.info("Starting ChatApp application", 
                       mysql_uri=MYSQL_URI.split('@')[1] if '@' in MYSQL_URI else "unknown")

    # Skip database connection attempts during testing
    if not app.config.get('TESTING', False):
        while True:
            try:
                with app.app_context():
                    db.create_all()
                    # Set initial database connection status
                    if hasattr(app, 'metrics') and 'database_connection' in app.metrics:
                        app.metrics['database_connection'].set(1)
                    app.logger.info("Database connection established successfully")
                break
            except OperationalError as e:
                app.logger.error("Failed to connect to MySQL database", 
                               error=str(e), retry_in_seconds=5)
                if hasattr(app, 'metrics') and 'database_connection' in app.metrics:
                    app.metrics['database_connection'].set(0)
                time.sleep(5)

    from routes import register_routes
    register_routes(app, db)

    # Add request logging middleware only if not testing
    if not app.config.get('TESTING', False):
        @app.before_request
        def log_request_info():
            app.logger.info("Incoming request", 
                           method=request.method,
                           path=request.path,
                           remote_addr=request.remote_addr)

        @app.after_request
        def log_response_info(response):
            app.logger.info("Request completed",
                           method=request.method,
                           path=request.path,
                           status_code=response.status_code,
                           content_length=response.content_length)
            return response

    return app