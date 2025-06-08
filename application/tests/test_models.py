import unittest
from datetime import datetime, timezone
from flask import Flask
from models import db, Chat


class TestChatModel(unittest.TestCase):
    """Test cases for Chat model"""
    
    def setUp(self):
        """Set up test environment"""
        # Create minimal Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        db.init_app(self.app)
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create tables
        db.create_all()
        
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_chat_creation(self):
        """Test creating a Chat instance"""
        chat = Chat(
            room='test_room',
            date='2025-05-26',
            time='12:00:00',
            username='test_user',
            message='Hello, World!'
        )
        
        self.assertEqual(chat.room, 'test_room')
        self.assertEqual(chat.username, 'test_user')
        self.assertEqual(chat.message, 'Hello, World!')
        self.assertEqual(chat.date, '2025-05-26')
        self.assertEqual(chat.time, '12:00:00')
        
    def test_chat_to_dict(self):
        """Test Chat to_dict method"""
        chat = Chat(
            room='test_room',
            date='2025-05-26',
            time='12:00:00',
            username='test_user',
            message='Hello, World!'
        )
        
        expected_dict = {
            'room': 'test_room',
            'date': '2025-05-26',
            'time': '12:00:00',
            'username': 'test_user',
            'message': 'Hello, World!'
        }
        
        self.assertEqual(chat.to_dict(), expected_dict)
        
    def test_chat_database_operations(self):
        """Test basic database operations"""
        # Create a chat entry
        chat = Chat(
            room='test_room',
            date='2025-05-26',
            time='12:00:00',
            username='test_user',
            message='Test message'
        )
        
        # Add to database
        db.session.add(chat)
        db.session.commit()
        
        # Retrieve from database
        retrieved_chat = db.session.execute(
            db.select(Chat).filter_by(room='test_room')
        ).scalar_one()
        
        self.assertEqual(retrieved_chat.username, 'test_user')
        self.assertEqual(retrieved_chat.message, 'Test message')
        self.assertIsNotNone(retrieved_chat.id)
        
    def test_multiple_messages_same_room(self):
        """Test multiple messages in the same room"""
        messages = [
            Chat(room='general', date='2025-05-26', time='12:00:00', 
                 username='user1', message='First message'),
            Chat(room='general', date='2025-05-26', time='12:01:00', 
                 username='user2', message='Second message'),
            Chat(room='general', date='2025-05-26', time='12:02:00', 
                 username='user1', message='Third message')
        ]
        
        for msg in messages:
            db.session.add(msg)
        db.session.commit()
        
        # Retrieve all messages from room
        room_messages = db.session.execute(
            db.select(Chat).filter_by(room='general')
        ).scalars().all()
        
        self.assertEqual(len(room_messages), 3)
        self.assertEqual(room_messages[0].username, 'user1')
        self.assertEqual(room_messages[1].username, 'user2')
        
    def test_different_rooms(self):
        """Test messages in different rooms are separate"""
        # Add messages to different rooms
        chat1 = Chat(room='room1', date='2025-05-26', time='12:00:00', 
                     username='user1', message='Room 1 message')
        chat2 = Chat(room='room2', date='2025-05-26', time='12:00:00', 
                     username='user1', message='Room 2 message')
        
        db.session.add(chat1)
        db.session.add(chat2)
        db.session.commit()
        
        # Check room1 messages
        room1_messages = db.session.execute(
            db.select(Chat).filter_by(room='room1')
        ).scalars().all()
        
        # Check room2 messages
        room2_messages = db.session.execute(
            db.select(Chat).filter_by(room='room2')
        ).scalars().all()
        
        self.assertEqual(len(room1_messages), 1)
        self.assertEqual(len(room2_messages), 1)
        self.assertEqual(room1_messages[0].message, 'Room 1 message')
        self.assertEqual(room2_messages[0].message, 'Room 2 message')
        
    def test_chat_string_fields(self):
        """Test Chat model string field constraints"""
        # Test with longer strings
        long_username = 'a' * 50  # Max length
        long_room = 'b' * 50      # Max length
        long_message = 'c' * 1000  # Should work with TEXT field
        
        chat = Chat(
            room=long_room,
            date='2025-05-26',
            time='12:00:00',
            username=long_username,
            message=long_message
        )
        
        db.session.add(chat)
        db.session.commit()
        
        # Retrieve and verify
        retrieved = db.session.execute(
            db.select(Chat).filter_by(room=long_room)
        ).scalar_one()
        
        self.assertEqual(len(retrieved.username), 50)
        self.assertEqual(len(retrieved.message), 1000)


if __name__ == '__main__':
    unittest.main()