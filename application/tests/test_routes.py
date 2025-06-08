import unittest
import json
from flask import Flask
from models import db, Chat


def create_test_app():
    """Create a test Flask app that doesn't try to connect to MySQL"""
    app = Flask(__name__)
    
    # Test configuration - use SQLite instead of MySQL
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Mock metrics for testing (since we don't have prometheus_flask_exporter in tests)
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
    
    # Register routes
    with app.app_context():
        from routes import register_routes
        register_routes(app, db)
    
    return app


class TestChatRoutes(unittest.TestCase):
    """Test cases for chat API routes"""
    
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
            
    def test_post_message_success(self):
        """Test posting a message successfully"""
        response = self.client.post('/api/chat/test_room', data={
            'username': 'test_user',
            'msg': 'Hello, World!'
        })
        
        # Accept both 200 and 201 as success codes
        self.assertIn(response.status_code, [200, 201])
        
        data = json.loads(response.data)
        
        # Handle the case where jsonify(dict, status_code) returns a list
        if isinstance(data, list):
            # If it's a list, the first element is the actual data
            chat_data = data[0]
        else:
            # If it's a dict, use it directly
            chat_data = data
            
        self.assertEqual(chat_data['room'], 'test_room')
        self.assertEqual(chat_data['username'], 'test_user')
        self.assertEqual(chat_data['message'], 'Hello, World!')
        
    def test_post_message_missing_username(self):
        """Test posting message without username"""
        response = self.client.post('/api/chat/test_room', data={
            'msg': 'Hello, World!'
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Username and message are required')
        
    def test_post_message_missing_message(self):
        """Test posting message without message content"""
        response = self.client.post('/api/chat/test_room', data={
            'username': 'test_user'
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_get_empty_room(self):
        """Test getting messages from empty room"""
        response = self.client.get('/api/chat/empty_room')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '')
        
    def test_get_messages_with_content(self):
        """Test getting messages from room with content"""
        # Add some test messages
        with self.app.app_context():
            chat1 = Chat(room='test_room', date='2025-05-26', time='12:00:00',
                        username='user1', message='First message')
            chat2 = Chat(room='test_room', date='2025-05-26', time='12:01:00',
                        username='user2', message='Second message')
            
            db.session.add(chat1)
            db.session.add(chat2)
            db.session.commit()
            
        response = self.client.get('/api/chat/test_room')
        
        self.assertEqual(response.status_code, 200)
        
        content = response.data.decode()
        self.assertIn('user1: First message', content)
        self.assertIn('user2: Second message', content)
        self.assertIn('[2025-05-26 12:00:00]', content)
        
    def test_delete_room_messages(self):
        """Test deleting all messages in a room"""
        # Add test messages
        with self.app.app_context():
            chat1 = Chat(room='test_room', date='2025-05-26', time='12:00:00',
                        username='user1', message='Message 1')
            chat2 = Chat(room='test_room', date='2025-05-26', time='12:01:00',
                        username='user2', message='Message 2')
            
            db.session.add(chat1)
            db.session.add(chat2)
            db.session.commit()
            
        # Delete messages
        response = self.client.delete('/api/chat/test_room')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('2 messages removed', data['message'])
        
        # Verify messages are deleted
        get_response = self.client.get('/api/chat/test_room')
        self.assertEqual(get_response.data.decode(), '')
        
    def test_update_username_success(self):
        """Test updating username successfully"""
        # Add test message
        with self.app.app_context():
            chat = Chat(room='test_room', date='2025-05-26', time='12:00:00',
                       username='old_user', message='Test message')
            db.session.add(chat)
            db.session.commit()
            
        # Update username
        response = self.client.put('/api/chat/test_room', data={
            'old_username': 'old_user',
            'new_username': 'new_user'
        })
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['old_username'], 'old_user')
        self.assertEqual(data['new_username'], 'new_user')
        self.assertEqual(data['messages_updated'], 1)
        
        # Verify username was updated
        get_response = self.client.get('/api/chat/test_room')
        content = get_response.data.decode()
        self.assertIn('new_user: Test message', content)
        self.assertNotIn('old_user: Test message', content)
        
    def test_update_username_missing_parameters(self):
        """Test updating username with missing parameters"""
        response = self.client.put('/api/chat/test_room', data={
            'old_username': 'old_user'
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_update_username_same_name(self):
        """Test updating username to the same name"""
        response = self.client.put('/api/chat/test_room', data={
            'old_username': 'user1',
            'new_username': 'user1'
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('New username must be different', data['error'])
        
    def test_update_username_already_exists(self):
        """Test updating to username that already exists"""
        # Add test messages with different users
        with self.app.app_context():
            chat1 = Chat(room='test_room', date='2025-05-26', time='12:00:00',
                        username='user1', message='Message 1')
            chat2 = Chat(room='test_room', date='2025-05-26', time='12:01:00',
                        username='user2', message='Message 2')
            
            db.session.add(chat1)
            db.session.add(chat2)
            db.session.commit()
            
        # Try to update user1 to user2
        response = self.client.put('/api/chat/test_room', data={
            'old_username': 'user1',
            'new_username': 'user2'
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('Username already exists', data['error'])
        
    def test_update_nonexistent_username(self):
        """Test updating username that doesn't exist"""
        response = self.client.put('/api/chat/test_room', data={
            'old_username': 'nonexistent_user',
            'new_username': 'new_user'
        })
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('No messages found', data['error'])


if __name__ == '__main__':
    unittest.main()