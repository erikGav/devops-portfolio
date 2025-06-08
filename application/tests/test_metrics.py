import unittest
import json
from flask import Flask
from models import db, Chat
from prometheus_flask_exporter import PrometheusMetrics



def create_test_app():
    """Create a test Flask app that doesn't try to connect to MySQL"""
    app = Flask(__name__)
    
    # Test configuration - use SQLite instead of MySQL
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    metrics = PrometheusMetrics(app)
    
    # Register routes
    with app.app_context():
        from routes import register_routes
        register_routes(app, db)
    
    return app


class TestMetricsEndpoint(unittest.TestCase):
    """Test cases for metrics endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = create_test_app()
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            
    def test_prometheus_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        response = self.client.get('/metrics')
        
        self.assertEqual(response.status_code, 200)
        
        # Should return Prometheus format (text/plain)
        content_type = response.headers.get('Content-Type', '')
        self.assertIn('text/plain', content_type)
        
        # Should contain basic Prometheus metrics
        content = response.data.decode()
        self.assertIn('flask_http_request_total', content)
        
    def test_json_metrics_endpoint_empty_database(self):
        """Test JSON metrics endpoint with empty database"""
        response = self.client.get('/metrics/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        
        # Check structure
        self.assertIn('timestamp', data)
        self.assertIn('system_health', data)
        self.assertIn('usage_stats', data)
        self.assertIn('top_rooms', data)
        self.assertIn('top_users', data)
        
        # Check empty database stats
        self.assertEqual(data['system_health']['database_status'], 'connected')
        self.assertEqual(data['usage_stats']['total_messages'], 0)
        self.assertEqual(data['usage_stats']['total_rooms'], 0)
        self.assertEqual(data['usage_stats']['total_users'], 0)
        self.assertEqual(len(data['top_rooms']), 0)
        self.assertEqual(len(data['top_users']), 0)
        
    def test_json_metrics_endpoint_with_data(self):
        """Test JSON metrics endpoint with sample data"""
        # Add test data
        with self.app.app_context():
            messages = [
                Chat(room='general', date='2025-05-26', time='12:00:00',
                     username='alice', message='Hello'),
                Chat(room='general', date='2025-05-26', time='12:01:00',
                     username='bob', message='Hi there'),
                Chat(room='random', date='2025-05-26', time='12:02:00',
                     username='alice', message='Random message'),
                Chat(room='general', date='2025-05-26', time='12:03:00',
                     username='charlie', message='Good morning'),
            ]
            
            for msg in messages:
                db.session.add(msg)
            db.session.commit()
            
        response = self.client.get('/metrics/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        
        # Check counts
        self.assertEqual(data['usage_stats']['total_messages'], 4)
        self.assertEqual(data['usage_stats']['total_rooms'], 2)
        self.assertEqual(data['usage_stats']['total_users'], 3)
        
        # Check averages
        self.assertEqual(data['usage_stats']['avg_messages_per_room'], 2.0)
        self.assertAlmostEqual(data['usage_stats']['avg_messages_per_user'], 1.33, places=2)
        
        # Check top rooms
        self.assertEqual(len(data['top_rooms']), 2)
        self.assertEqual(data['top_rooms'][0]['room'], 'general')
        self.assertEqual(data['top_rooms'][0]['message_count'], 3)
        
        # Check top users
        self.assertEqual(len(data['top_users']), 3)
        self.assertEqual(data['top_users'][0]['username'], 'alice')
        self.assertEqual(data['top_users'][0]['message_count'], 2)
        
    def test_json_metrics_today_filter(self):
        """Test JSON metrics filtering for today's activity"""
        # Add messages from different dates
        with self.app.app_context():
            messages = [
                Chat(room='test', date='2025-05-26', time='12:00:00',
                     username='user1', message='Today message'),
                Chat(room='test', date='2025-05-25', time='12:00:00',
                     username='user2', message='Yesterday message'),
            ]
            
            for msg in messages:
                db.session.add(msg)
            db.session.commit()
            
        response = self.client.get('/metrics/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        
        # Total should include all messages
        self.assertEqual(data['usage_stats']['total_messages'], 2)
        self.assertEqual(data['usage_stats']['total_users'], 2)
        
        # Today's stats depend on current date, so we check they exist
        self.assertIn('messages_today', data['usage_stats'])
        self.assertIn('active_users_today', data['usage_stats'])
        self.assertIn('recent_messages_7d', data['usage_stats'])
        
    def test_json_metrics_system_health(self):
        """Test system health information in JSON metrics"""
        response = self.client.get('/metrics/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        
        # Check system health
        health = data['system_health']
        self.assertEqual(health['database_status'], 'connected')
        self.assertIn('total_records', health)
        self.assertIsInstance(health['total_records'], int)
        
    def test_backward_compatibility_metrics_endpoint(self):
        """Test that /metrics endpoint still exists and returns Prometheus format"""
        response = self.client.get('/metrics')
        
        self.assertEqual(response.status_code, 200)
        
        # Should be text/plain for Prometheus
        content_type = response.headers.get('Content-Type', '')
        self.assertTrue(
            'text/plain' in content_type or 'text/plain' in str(response.mimetype),
            f"Expected text/plain, got {content_type}"
        )


if __name__ == '__main__':
    unittest.main()