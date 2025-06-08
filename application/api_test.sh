#!/bin/bash

# API Endpoint Testing Script for ChatApp
# This script tests all endpoints to generate logs

BASE_URL="http://localhost:8080"
DEFAULT_ITERATIONS=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to generate random data
generate_random_string() {
    cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w ${1:-10} | head -n 1
}

generate_random_message() {
    local messages=(
        "Hello world! This is a test message."
        "Testing the chat application with some random text."
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        "This is message number $RANDOM for testing purposes."
        "Chat application load testing in progress..."
        "Random message with emoji! 🚀 🎉 ✨"
        "Testing special characters: !@#$%^&*()"
        "Multi-word test message with various lengths."
        "Short msg"
        "This is a much longer message to test how the application handles messages of varying lengths and content types."
    )
    echo "${messages[$((RANDOM % ${#messages[@]}))]}"
}

# Parse command line arguments
ITERATIONS=$DEFAULT_ITERATIONS
ROOM_PREFIX="testroom"
USERNAME_PREFIX="testuser"

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--iterations)
            ITERATIONS="$2"
            shift 2
            ;;
        -u|--url)
            BASE_URL="$2"
            shift 2
            ;;
        -r|--room-prefix)
            ROOM_PREFIX="$2"
            shift 2
            ;;
        --username-prefix)
            USERNAME_PREFIX="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -n, --iterations N        Number of iterations (default: $DEFAULT_ITERATIONS)"
            echo "  -u, --url URL            Base URL (default: $BASE_URL)"
            echo "  -r, --room-prefix PREFIX Room name prefix (default: $ROOM_PREFIX)"
            echo "  --username-prefix PREFIX Username prefix (default: $USERNAME_PREFIX)"
            echo "  -h, --help               Show this help message"
            echo ""
            echo "Example: $0 -n 50 -u http://localhost:8080"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

print_status $BLUE "🚀 Starting API endpoint testing with $ITERATIONS iterations"
print_status $BLUE "📍 Target URL: $BASE_URL"
echo ""

# Test counter
total_tests=0
successful_tests=0
failed_tests=0

# Function to make request and track results
make_request() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4
    
    total_tests=$((total_tests + 1))
    
    # Build and display the curl command
    if [[ -n "$data" ]]; then
        curl_command="curl -X $method \"$url\" -d \"$data\" -H \"Content-Type: application/x-www-form-urlencoded\""
        response=$(curl -s -w "%{http_code}" -X "$method" "$url" -d "$data" -H "Content-Type: application/x-www-form-urlencoded")
    else
        curl_command="curl -X $method \"$url\""
        response=$(curl -s -w "%{http_code}" -X "$method" "$url")
    fi
    
    http_code="${response: -3}"
    response_body="${response%???}"
    
    # Print the curl command
    print_status $BLUE "🔧 $curl_command"
    
    if [[ "$http_code" =~ ^[2-3][0-9][0-9]$ ]]; then
        print_status $GREEN "✅ $description - HTTP $http_code"
        successful_tests=$((successful_tests + 1))
    else
        print_status $RED "❌ $description - HTTP $http_code"
        if [[ -n "$response_body" ]]; then
            echo "   Response: $response_body"
        fi
        failed_tests=$((failed_tests + 1))
    fi
    
    echo ""  # Add spacing between requests
}

# Test health endpoint first
print_status $YELLOW "🏥 Testing health endpoint..."
make_request "GET" "$BASE_URL/health" "" "Health check"

# Test metrics endpoints
print_status $YELLOW "📊 Testing metrics endpoints..."
make_request "GET" "$BASE_URL/metrics" "" "Prometheus metrics"
make_request "GET" "$BASE_URL/metrics/json" "" "JSON metrics"

echo ""
print_status $YELLOW "🗨️  Starting chat endpoint tests..."

# Main testing loop
for i in $(seq 1 $ITERATIONS); do
    echo ""
    print_status $BLUE "--- Iteration $i/$ITERATIONS ---"
    
    # Generate test data for this iteration
    room="${ROOM_PREFIX}$((RANDOM % 5 + 1))"  # Use 5 different rooms
    username="${USERNAME_PREFIX}$((RANDOM % 10 + 1))"  # Use 10 different users
    message=$(generate_random_message)
    
    # 1. POST - Send new message
    post_data="username=$username&msg=$message"
    make_request "POST" "$BASE_URL/api/chat/$room" "$post_data" "POST message to room '$room' by user '$username'"
    
    # 2. GET - Retrieve messages (every few iterations)
    if [[ $((i % 3)) -eq 0 ]]; then
        make_request "GET" "$BASE_URL/api/chat/$room" "" "GET messages from room '$room'"
    fi
    
    # 3. PUT - Update username (less frequently)
    if [[ $((i % 7)) -eq 0 ]]; then
        old_username="$username"
        new_username="${USERNAME_PREFIX}_updated_$((RANDOM % 100))"
        put_data="old_username=$old_username&new_username=$new_username"
        make_request "PUT" "$BASE_URL/api/chat/$room" "$put_data" "PUT update username from '$old_username' to '$new_username' in room '$room'"
    fi
    
    # 4. DELETE - Clear room (very infrequently)
    if [[ $((i % 20)) -eq 0 ]]; then
        delete_room="${ROOM_PREFIX}_delete_test"
        # First add a message to delete
        make_request "POST" "$BASE_URL/api/chat/$delete_room" "username=temp_user&msg=Message to be deleted" "POST message before DELETE"
        make_request "DELETE" "$BASE_URL/api/chat/$delete_room" "" "DELETE all messages from room '$delete_room'"
    fi
    
    # 5. Health check (occasionally)
    if [[ $((i % 10)) -eq 0 ]]; then
        make_request "GET" "$BASE_URL/health" "" "Health check (iteration $i)"
    fi
    
    # 6. Metrics check (occasionally)
    if [[ $((i % 15)) -eq 0 ]]; then
        make_request "GET" "$BASE_URL/metrics/json" "" "JSON metrics (iteration $i)"
    fi
    
    # Small delay to prevent overwhelming the server
    sleep 0.1
done

# Test some error conditions
echo ""
print_status $YELLOW "🚫 Testing error conditions..."

# Test missing parameters
make_request "POST" "$BASE_URL/api/chat/errortest" "username=testuser" "POST with missing message (should fail)"
make_request "POST" "$BASE_URL/api/chat/errortest" "msg=test message" "POST with missing username (should fail)"
make_request "PUT" "$BASE_URL/api/chat/errortest" "old_username=nonexistent" "PUT with missing new_username (should fail)"
make_request "PUT" "$BASE_URL/api/chat/errortest" "old_username=user1&new_username=user1" "PUT with same username (should fail)"

# Test non-existent room operations
make_request "PUT" "$BASE_URL/api/chat/nonexistentroom" "old_username=nonexistent&new_username=newuser" "PUT in non-existent room (should fail)"

# Test invalid endpoints
make_request "GET" "$BASE_URL/api/invalid/endpoint" "" "GET invalid endpoint (should fail)"
make_request "POST" "$BASE_URL/invalid" "" "POST to invalid path (should fail)"

# Final summary
echo ""
print_status $BLUE "=============================================="
print_status $BLUE "🏁 Testing completed!"
print_status $BLUE "=============================================="
echo ""
print_status $GREEN "📈 Total tests: $total_tests"
print_status $GREEN "✅ Successful: $successful_tests"
print_status $RED "❌ Failed: $failed_tests"

if [[ $failed_tests -eq 0 ]]; then
    print_status $GREEN "🎉 All tests passed!"
else
    success_rate=$((successful_tests * 100 / total_tests))
    print_status $YELLOW "📊 Success rate: ${success_rate}%"
fi

echo ""
print_status $BLUE "💡 Tips:"
echo "   - Check your application logs for the generated entries"
echo "   - Visit $BASE_URL/metrics/json to see updated metrics"
echo "   - Visit $BASE_URL/health to verify system health"
echo ""
print_status $BLUE "🔄 To run again with different parameters:"
echo "   $0 -n 100 -u http://localhost:8080"
