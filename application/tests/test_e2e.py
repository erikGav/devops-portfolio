#!/usr/bin/env python3
"""
Simple API testing script for live ChatApp instance
Tests the actual running application at http://app:5000
"""

import requests
import json
import time
import sys
from datetime import datetime


class ChatAppAPITester:
    def __init__(self, base_url="http://app:5000"):
        self.base_url = base_url
        self.test_room = f"api_test_{int(time.time())}"  # Unique room for testing
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        
    def test_health_check(self):
        """Test health endpoint"""
        self.log("Testing health check endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log("✅ Health check passed", "PASS")
                    return True
                else:
                    self.log(f"❌ Health check failed: {data}", "FAIL")
                    return False
            else:
                self.log(f"❌ Health endpoint returned {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Health check error: {e}", "ERROR")
            return False
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        self.log("Testing metrics endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/metrics/json")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['system_health', 'usage_stats', 'top_rooms', 'top_users']
                
                if all(field in data for field in required_fields):
                    self.log("✅ Metrics endpoint working", "PASS")
                    self.log(f"   Total messages: {data['usage_stats']['total_messages']}")
                    self.log(f"   Total users: {data['usage_stats']['total_users']}")
                    return True
                else:
                    self.log(f"❌ Metrics missing required fields", "FAIL")
                    return False
            else:
                self.log(f"❌ Metrics endpoint returned {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Metrics error: {e}", "ERROR")
            return False
    
    def test_send_message(self, username, message):
        """Test sending a message"""
        self.log(f"Sending message as {username}: '{message}'")
        
        try:
            response = requests.post(f"{self.base_url}/api/chat/{self.test_room}", data={
                'username': username,
                'msg': message
            })
            
            if response.status_code in [200, 201]:
                self.log("✅ Message sent successfully", "PASS")
                return True
            else:
                self.log(f"❌ Failed to send message: {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Send message error: {e}", "ERROR")
            return False
    
    def test_get_messages(self, expected_count=None):
        """Test retrieving messages"""
        self.log("Retrieving messages...")
        
        try:
            response = requests.get(f"{self.base_url}/api/chat/{self.test_room}")
            
            if response.status_code == 200:
                content = response.text
                if not content.strip():
                    message_count = 0
                else:
                    message_count = len([line for line in content.split('\n') if line.strip()])
                
                self.log(f"✅ Retrieved {message_count} messages", "PASS")
                
                if expected_count is not None:
                    if message_count == expected_count:
                        self.log(f"✅ Message count matches expected ({expected_count})", "PASS")
                        return True
                    else:
                        self.log(f"❌ Expected {expected_count} messages, got {message_count}", "FAIL")
                        return False
                
                return True
            else:
                self.log(f"❌ Failed to get messages: {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Get messages error: {e}", "ERROR")
            return False
    
    def test_update_username(self, old_username, new_username):
        """Test updating username"""
        self.log(f"Updating username: {old_username} -> {new_username}")
        
        try:
            response = requests.put(f"{self.base_url}/api/chat/{self.test_room}", data={
                'old_username': old_username,
                'new_username': new_username
            })
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Username updated: {data.get('messages_updated', 0)} messages affected", "PASS")
                return True
            else:
                self.log(f"❌ Failed to update username: {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Update username error: {e}", "ERROR")
            return False
    
    def test_clear_chat(self):
        """Test clearing chat"""
        self.log("Clearing chat...")
        
        try:
            response = requests.delete(f"{self.base_url}/api/chat/{self.test_room}")
            
            if response.status_code == 200:
                self.log("✅ Chat cleared successfully", "PASS")
                return True
            else:
                self.log(f"❌ Failed to clear chat: {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Clear chat error: {e}", "ERROR")
            return False
    
    def run_complete_workflow_test(self):
        """Run a complete end-to-end workflow test"""
        self.log("=" * 60)
        self.log("Starting Complete API Workflow Test")
        self.log(f"Test room: {self.test_room}")
        self.log("=" * 60)
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Health check
        total_tests += 1
        if self.test_health_check():
            tests_passed += 1
        
        # Test 2: Metrics
        total_tests += 1
        if self.test_metrics_endpoint():
            tests_passed += 1
        
        # Test 3: Send messages
        total_tests += 1
        if self.test_send_message("alice", "Hello everyone!"):
            tests_passed += 1
        
        total_tests += 1
        if self.test_send_message("alice", "How is everyone doing?"):
            tests_passed += 1
        
        total_tests += 1
        if self.test_send_message("bob", "Hi Alice! Doing great!"):
            tests_passed += 1
        
        # Test 4: Get messages (expect 3)
        total_tests += 1
        if self.test_get_messages(expected_count=3):
            tests_passed += 1
        
        # Test 5: Update username
        total_tests += 1
        if self.test_update_username("alice", "alice_smith"):
            tests_passed += 1
        
        # Test 6: Verify username update (still 3 messages)
        total_tests += 1
        if self.test_get_messages(expected_count=3):
            tests_passed += 1
        
        # Test 7: Send another message
        total_tests += 1
        if self.test_send_message("bob", "Nice to meet you Alice Smith!"):
            tests_passed += 1
        
        # Test 8: Clear chat
        total_tests += 1
        if self.test_clear_chat():
            tests_passed += 1
        
        # Test 9: Verify chat is empty
        total_tests += 1
        if self.test_get_messages(expected_count=0):
            tests_passed += 1
        
        # Final results
        self.log("=" * 60)
        self.log(f"TEST RESULTS: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            self.log("🎉 ALL TESTS PASSED! Your ChatApp API is working perfectly!", "SUCCESS")
            return True
        else:
            self.log(f"❌ {total_tests - tests_passed} tests failed", "FAIL")
            return False
    
    def run_error_handling_tests(self):
        """Test error conditions"""
        self.log("=" * 60)
        self.log("Testing Error Handling")
        self.log("=" * 60)
        
        tests_passed = 0
        total_tests = 4
        
        # Test 1: Send message without username
        self.log("Testing message without username...")
        try:
            response = requests.post(f"{self.base_url}/api/chat/{self.test_room}", data={
                'msg': 'Message without username'
            })
            if response.status_code == 400:
                self.log("✅ Correctly rejected message without username", "PASS")
                tests_passed += 1
            else:
                self.log(f"❌ Expected 400, got {response.status_code}", "FAIL")
        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
        
        # Test 2: Send message without content
        self.log("Testing message without content...")
        try:
            response = requests.post(f"{self.base_url}/api/chat/{self.test_room}", data={
                'username': 'testuser'
            })
            if response.status_code == 400:
                self.log("✅ Correctly rejected message without content", "PASS")
                tests_passed += 1
            else:
                self.log(f"❌ Expected 400, got {response.status_code}", "FAIL")
        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
        
        # Test 3: Update non-existent username
        self.log("Testing update of non-existent username...")
        try:
            response = requests.put(f"{self.base_url}/api/chat/{self.test_room}", data={
                'old_username': 'nonexistent',
                'new_username': 'newname'
            })
            if response.status_code == 404:
                self.log("✅ Correctly rejected non-existent username update", "PASS")
                tests_passed += 1
            else:
                self.log(f"❌ Expected 404, got {response.status_code}", "FAIL")
        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
        
        # Test 4: Update with missing parameters
        self.log("Testing update with missing parameters...")
        try:
            response = requests.put(f"{self.base_url}/api/chat/{self.test_room}", data={
                'old_username': 'user1'
            })
            if response.status_code == 400:
                self.log("✅ Correctly rejected incomplete update request", "PASS")
                tests_passed += 1
            else:
                self.log(f"❌ Expected 400, got {response.status_code}", "FAIL")
        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
        
        self.log(f"Error handling tests: {tests_passed}/{total_tests} passed")
        return tests_passed == total_tests


def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://app:5000"
    
    print(f"🚀 ChatApp API Tester")
    print(f"Testing against: {base_url}")
    print()
    
    tester = ChatAppAPITester(base_url)
    
    # Run main workflow test
    workflow_success = tester.run_complete_workflow_test()
    
    print()
    
    # Run error handling tests
    error_success = tester.run_error_handling_tests()
    
    print()
    print("=" * 60)
    if workflow_success and error_success:
        print("🎉 ALL API TESTS PASSED! Your ChatApp is working perfectly!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()