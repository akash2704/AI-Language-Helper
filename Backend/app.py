import os
import sqlite3
import datetime
import jwt
import uuid
import json
from functools import wraps
from flask import Flask, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from dotenv import load_dotenv

from chatbot import (
    init_db as init_mistakes_db,
    model,
    scene_prompt,
    chat_prompt,
    feedback_prompt,
    parse_output,
    record_mistake,
    get_feedback
)

# --- Load environment variables ---
load_dotenv()

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6')
CORS(app, resources={r"/*": {"origins": "*"}})

# --- User DB Initialization ---
def init_user_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def init_session_db():
    conn = sqlite3.connect('sessions.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            target_lang TEXT NOT NULL,
            source_lang TEXT NOT NULL,
            level TEXT NOT NULL,
            conversation TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- Run DB Initializations ---
init_user_db()
init_mistakes_db()
init_session_db()
print("✅ User, Mistakes, and Session databases initialized.")

# --- Flask-Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'message': 'Authentication required'}), 401

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[3])
    return None

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
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE id = ?", (data['user_id'],))
            current_user = c.fetchone()
            conn.close()
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
    hashed_password = generate_password_hash(password)
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                  (username, hashed_password, email))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username or email already exists'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[2], password):
        user_obj = User(user[0], user[1], user[3])
        login_user(user_obj)
        token = jwt.encode({
            'user_id': user[0],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.secret_key, algorithm="HS256")
        return jsonify({'token': token, 'message': 'Logged in successfully'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
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
    session_id = str(uuid.uuid4())

    scene_output = model.generate_content(scene_prompt.format(
        target_lang=target_lang,
        source_lang=source_lang,
        level=level
    )).text
    response, corrections = parse_output(scene_output)

    conn = sqlite3.connect('sessions.db')
    c = conn.cursor()
    c.execute("INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?)",
              (session_id, user_id, target_lang, source_lang, level,
               json.dumps([{'bot': response}]), datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({
        'session_id': session_id,
        'response': response,
        'corrections': corrections
    }), 200

@app.route('/api/chat', methods=['POST'])
@token_required
def chat():
    data = request.get_json()
    user_input = data.get('user_input')
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'message': 'Missing session ID'}), 400

    conn = sqlite3.connect('sessions.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    session_data = c.fetchone()
    conn.close()

    if not session_data:
        return jsonify({'message': 'Invalid session ID'}), 400

    target_lang = session_data[2]
    source_lang = session_data[3]
    conversation = json.loads(session_data[5])

    chat_output = model.generate_content(chat_prompt.format(
        target_lang=target_lang,
        source_lang=source_lang,
        user_input=user_input
    )).text
    response, corrections = parse_output(chat_output)

    conversation.append({'user': user_input, 'bot': response})
    record_mistake(user_input, corrections, source_lang)

    conn = sqlite3.connect('sessions.db')
    c = conn.cursor()
    c.execute("UPDATE sessions SET conversation = ? WHERE id = ?",
              (json.dumps(conversation), session_id))
    conn.commit()
    conn.close()

    return jsonify({'response': response, 'corrections': corrections}), 200

@app.route('/api/feedback', methods=['GET'])
@token_required
def feedback():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'message': 'Missing session ID'}), 400

    conn = sqlite3.connect('sessions.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    session_data = c.fetchone()
    conn.close()

    if not session_data:
        return jsonify({'message': 'Invalid session ID'}), 400

    source_lang = session_data[3]
    feedback_text = get_feedback(source_lang)
    return jsonify({'feedback': feedback_text}), 200

# --- Main ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
