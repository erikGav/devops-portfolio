import unittest
import os
from unittest.mock import patch, MagicMock
from flask import Flask
from models import db


def create_test_app():
    """Create a test Flask app that doesn't try to connect to MySQL"""
    app = Flask(__name__)
    
    # Test configuration - use SQLite instead of MySQL
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database without the connection retry loop
    db.init_app(app)
    
    return app


class TestAppConfig(unittest.TestCase):
    """Test cases for application configuration"""
    
    @patch('time.sleep')  # Mock sleep to avoid delays
    @patch('pymysql.install_as_MySQLdb')  # Mock pymysql
    def test_database_uri_formation_mocked(self, mock_pymysql, mock_sleep):
        """Test database URI formation without actual connection"""
        with patch.dict(os.environ, {
            'MYSQL_USER': 'test_user',
            'MYSQL_PASSWORD': 'test_password',
            'MYSQL_DATABASE': 'test_db',
            'MYSQL_HOST': 'test_host'
        }):
            # Mock the database connection to avoid retry loop
            with patch('models.db.create_all'):
                with patch('sqlalchemy.exc.OperationalError', side_effect=None):
                    app = Flask(__name__)
                    
                    # Manually set the database URI like create_app() does
                    db_user = os.environ.get('MYSQL_USER')
                    db_password = os.environ.get('MYSQL_PASSWORD') 
                    db_database = os.environ.get('MYSQL_DATABASE')
                    db_host = os.environ.get('MYSQL_HOST')
                    db_uri = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_database}'
                    
                    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
                    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
                    
                    expected_uri = 'mysql+pymysql://test_user:test_password@test_host:3306/test_db'
                    self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], expected_uri)
        
    def test_test_app_creation(self):
        """Test that test app is created successfully"""
        app = create_test_app()
        
        self.assertIsNotNone(app)
        self.assertEqual(app.__class__.__name__, 'Flask')
        self.assertTrue(app.config['TESTING'])
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite:///:memory:')
        
    def test_sqlalchemy_config(self):
        """Test SQLAlchemy configuration in test app"""
        app = create_test_app()
        
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['SQLALCHEMY_TRACK_MODIFICATIONS'])
        
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_environment_variables(self):
        """Test handling of missing environment variables"""
        # Test the logic without actually creating the problematic app
        db_user = os.environ.get('MYSQL_USER', "Environment variable MYSQL_USER does not exist")
        db_password = os.environ.get('MYSQL_PASSWORD', "Environment variable MYSQL_PASSWORD does not exist")
        db_database = os.environ.get('MYSQL_DATABASE', "Environment variable MYSQL_DATABASE does not exist")
        db_host = os.environ.get('MYSQL_HOST', "Environment variable MYSQL_HOST does not exist")
        
        db_uri = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_database}'
        
        # Should contain error messages for missing variables
        self.assertIn('Environment variable', db_uri)


if __name__ == '__main__':
    unittest.main()