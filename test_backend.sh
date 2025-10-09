#!/bin/bash

# AI Language Helper Backend Test Script

API_URL="https://r657yd9lrl.execute-api.ap-south-1.amazonaws.com"
TEST_USER="testuser_$(date +%s)"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASS="testpass123"

echo "🧪 Testing AI Language Helper Backend API"
echo "API URL: $API_URL"
echo "=========================================="

# Test 1: Health Check
echo "1️⃣ Testing Health Check..."
HEALTH=$(curl -s "$API_URL/health")
echo "Response: $HEALTH"
if [[ $HEALTH == *"healthy"* ]]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi
echo ""

# Test 2: User Registration
echo "2️⃣ Testing User Registration..."
REGISTER=$(curl -s -X POST "$API_URL/register" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$TEST_USER\",\"password\":\"$TEST_PASS\",\"email\":\"$TEST_EMAIL\"}")
echo "Response: $REGISTER"
if [[ $REGISTER == *"successfully"* ]]; then
    echo "✅ Registration passed"
else
    echo "❌ Registration failed"
    exit 1
fi
echo ""

# Test 3: User Login
echo "3️⃣ Testing User Login..."
LOGIN=$(curl -s -X POST "$API_URL/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$TEST_USER\",\"password\":\"$TEST_PASS\"}")
echo "Response: $LOGIN"
if [[ $LOGIN == *"token"* ]]; then
    TOKEN=$(echo $LOGIN | grep -o '"token":"[^"]*' | cut -d'"' -f4)
    echo "✅ Login passed - Token received"
else
    echo "❌ Login failed"
    exit 1
fi
echo ""

# Test 4: Token Verification
echo "4️⃣ Testing Token Verification..."
VERIFY=$(curl -s "$API_URL/api/verify_session" \
    -H "Authorization: Bearer $TOKEN")
echo "Response: $VERIFY"
if [[ $VERIFY == *"valid"* ]]; then
    echo "✅ Token verification passed"
else
    echo "❌ Token verification failed"
    exit 1
fi
echo ""

# Test 5: Start Session
echo "5️⃣ Testing Start Session..."
START_SESSION=$(curl -s -X POST "$API_URL/api/start_session" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"target_lang":"Spanish","source_lang":"English","level":"beginner"}')
echo "Response: $START_SESSION"
if [[ $START_SESSION == *"session_id"* ]]; then
    SESSION_ID=$(echo $START_SESSION | grep -o '"session_id":"[^"]*' | cut -d'"' -f4)
    echo "✅ Start session passed - Session ID: $SESSION_ID"
else
    echo "❌ Start session failed"
    exit 1
fi
echo ""

# Test 6: Chat
echo "6️⃣ Testing Chat..."
CHAT=$(curl -s -X POST "$API_URL/api/chat" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"user_input\":\"Hola, como estas?\",\"session_id\":\"$SESSION_ID\"}")
echo "Response: $CHAT"
if [[ $CHAT == *"response"* ]]; then
    echo "✅ Chat passed"
else
    echo "❌ Chat failed"
    exit 1
fi
echo ""

# Test 7: Feedback
echo "7️⃣ Testing Feedback..."
FEEDBACK=$(curl -s "$API_URL/api/feedback?session_id=$SESSION_ID" \
    -H "Authorization: Bearer $TOKEN")
echo "Response: $FEEDBACK"
if [[ $FEEDBACK == *"feedback"* ]]; then
    echo "✅ Feedback passed"
else
    echo "❌ Feedback failed"
    exit 1
fi
echo ""

# Test 8: Logout
echo "8️⃣ Testing Logout..."
LOGOUT=$(curl -s "$API_URL/logout")
echo "Response: $LOGOUT"
if [[ $LOGOUT == *"successfully"* ]]; then
    echo "✅ Logout passed"
else
    echo "❌ Logout failed"
fi
echo ""

echo "🎉 All tests completed successfully!"
echo "Backend API is working properly ✅"
