import os
import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Table names from environment
USERS_TABLE = os.getenv('DYNAMODB_TABLE_USERS')
SESSIONS_TABLE = os.getenv('DYNAMODB_TABLE_SESSIONS')
MISTAKES_TABLE = os.getenv('DYNAMODB_TABLE_MISTAKES')

def get_table(table_name):
    """Get DynamoDB table"""
    return dynamodb.Table(table_name)

# User operations
def create_user(username, password_hash, email):
    """Create a new user"""
    table = get_table(USERS_TABLE)
    user_id = str(uuid.uuid4())
    
    try:
        table.put_item(
            Item={
                'id': user_id,
                'username': username,
                'password': password_hash,
                'email': email,
                'created_at': datetime.now().isoformat()
            },
            ConditionExpression='attribute_not_exists(id)'
        )
        return user_id
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return None
        raise e

def get_user_by_username(username):
    """Get user by username"""
    table = get_table(USERS_TABLE)
    
    try:
        response = table.query(
            IndexName='username-index',
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={':username': username}
        )
        items = response.get('Items', [])
        return items[0] if items else None
    except ClientError:
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    table = get_table(USERS_TABLE)
    
    try:
        response = table.get_item(Key={'id': user_id})
        return response.get('Item')
    except ClientError:
        return None

def check_username_exists(username):
    """Check if username exists"""
    return get_user_by_username(username) is not None

def check_email_exists(email):
    """Check if email exists"""
    table = get_table(USERS_TABLE)
    
    try:
        response = table.query(
            IndexName='email-index',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        return len(response.get('Items', [])) > 0
    except ClientError:
        return False

# Session operations
def create_session(user_id, target_lang, source_lang, level, conversation):
    """Create a new session"""
    table = get_table(SESSIONS_TABLE)
    session_id = str(uuid.uuid4())
    
    try:
        table.put_item(
            Item={
                'id': session_id,
                'user_id': user_id,
                'target_lang': target_lang,
                'source_lang': source_lang,
                'level': level,
                'conversation': conversation,
                'created_at': datetime.now().isoformat()
            }
        )
        return session_id
    except ClientError:
        return None

def get_session(session_id):
    """Get session by ID"""
    table = get_table(SESSIONS_TABLE)
    
    try:
        response = table.get_item(Key={'id': session_id})
        return response.get('Item')
    except ClientError:
        return None

def update_session_conversation(session_id, conversation):
    """Update session conversation"""
    table = get_table(SESSIONS_TABLE)
    
    try:
        table.update_item(
            Key={'id': session_id},
            UpdateExpression='SET conversation = :conversation',
            ExpressionAttributeValues={':conversation': conversation}
        )
        return True
    except ClientError:
        return False

# Mistake operations
def create_mistake(user_input, corrections, language):
    """Record a mistake"""
    table = get_table(MISTAKES_TABLE)
    mistake_id = str(uuid.uuid4())
    
    try:
        table.put_item(
            Item={
                'id': mistake_id,
                'user_input': user_input,
                'corrections': corrections,
                'language': language,
                'created_at': datetime.now().isoformat()
            }
        )
        return mistake_id
    except ClientError:
        return None

def get_mistakes_by_language(language, limit=50):
    """Get mistakes by language"""
    table = get_table(MISTAKES_TABLE)
    
    try:
        response = table.query(
            IndexName='language-index',
            KeyConditionExpression='language = :language',
            ExpressionAttributeValues={':language': language},
            Limit=limit,
            ScanIndexForward=False  # Get most recent first
        )
        return response.get('Items', [])
    except ClientError:
        return []
