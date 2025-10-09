import os
import datetime
import jwt
import json
from functools import wraps
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

from chatbot import (
    model,
    scene_prompt,
    chat_prompt,
    parse_output,
    get_feedback
)
from db_utils import (
    create_user,
    get_user_by_username,
    get_user_by_id,
    check_username_exists,
    check_email_exists,
    create_session,
    get_session,
    update_session_conversation,
    create_mistake
)

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key')
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Token Auth Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        if token.startswith('Bearer '):
            token = token[7:]
        try:
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            current_user = get_user_by_id(data['user_id'])
            if not current_user:
                raise Exception
        except Exception:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated

# --- Auth Routes ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not all([username, password, email]):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if username or email already exists
    if check_username_exists(username):
        return jsonify({'message': 'Username already exists'}), 400
    
    if check_email_exists(email):
        return jsonify({'message': 'Email already exists'}), 400
    
    hashed_password = generate_password_hash(password)
    user_id = create_user(username, hashed_password, email)
    
    if user_id:
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'message': 'Registration failed'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = get_user_by_username(username)
    
    if user and check_password_hash(user['password'], password):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.secret_key, algorithm="HS256")
        return jsonify({'token': token, 'message': 'Logged in successfully'}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/logout', methods=['GET'])
def logout():
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/verify_session', methods=['GET'])
@token_required
def verify_session():
    return jsonify({'message': 'Token is valid'}), 200

# --- Chatbot Routes ---
@app.route('/api/start_session', methods=['POST'])
@token_required
def start_session():
    data = request.get_json()
    target_lang = data.get('target_lang')
    source_lang = data.get('source_lang')
    level = data.get('level')
    
    if not all([target_lang, source_lang, level]):
        return jsonify({'message': 'Missing required fields'}), 400

    token = request.headers.get('Authorization').replace('Bearer ', '')
    user_data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
    user_id = user_data['user_id']

    scene_output = model.generate_content(scene_prompt.format(
        target_lang=target_lang,
        source_lang=source_lang,
        level=level
    )).text
    response, corrections = parse_output(scene_output)

    conversation = [{'bot': response}]
    session_id = create_session(user_id, target_lang, source_lang, level, json.dumps(conversation))

    if session_id:
        return jsonify({
            'session_id': session_id,
            'response': response,
            'corrections': corrections
        }), 200
    else:
        return jsonify({'message': 'Failed to create session'}), 500

@app.route('/api/chat', methods=['POST'])
@token_required
def chat():
    data = request.get_json()
    user_input = data.get('user_input')
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'message': 'Missing session ID'}), 400

    session_data = get_session(session_id)
    
    if not session_data:
        return jsonify({'message': 'Invalid session ID'}), 400

    target_lang = session_data['target_lang']
    source_lang = session_data['source_lang']
    conversation = json.loads(session_data['conversation'])

    chat_output = model.generate_content(chat_prompt.format(
        target_lang=target_lang,
        source_lang=source_lang,
        user_input=user_input
    )).text
    response, corrections = parse_output(chat_output)

    conversation.append({'user': user_input, 'bot': response})
    
    # Record mistake if there are corrections
    if corrections:
        create_mistake(user_input, corrections, source_lang)

    # Update session
    update_session_conversation(session_id, json.dumps(conversation))

    return jsonify({'response': response, 'corrections': corrections}), 200

@app.route('/api/feedback', methods=['GET'])
@token_required
def feedback():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'message': 'Missing session ID'}), 400

    session_data = get_session(session_id)
    
    if not session_data:
        return jsonify({'message': 'Invalid session ID'}), 400

    source_lang = session_data['source_lang']
    feedback_text = get_feedback(source_lang)
    return jsonify({'feedback': feedback_text}), 200

# --- Health Check ---
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

# --- Main ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
