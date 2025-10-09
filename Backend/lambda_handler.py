import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

def handler(event, context):
    """AWS Lambda handler for Flask app"""
    try:
        # Import here to avoid circular imports
        from werkzeug.wrappers import Request
        from werkzeug.serving import WSGIRequestHandler
        from io import StringIO
        
        # Handle API Gateway event
        if 'httpMethod' in event:
            # Create WSGI environ from API Gateway event
            environ = {
                'REQUEST_METHOD': event.get('httpMethod', 'GET'),
                'PATH_INFO': event.get('path', '/'),
                'QUERY_STRING': '',
                'CONTENT_TYPE': '',
                'CONTENT_LENGTH': '',
                'SERVER_NAME': 'localhost',
                'SERVER_PORT': '80',
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'https',
                'wsgi.input': StringIO(),
                'wsgi.errors': StringIO(),
                'wsgi.multithread': False,
                'wsgi.multiprocess': True,
                'wsgi.run_once': False
            }
            
            # Add headers
            headers = event.get('headers', {})
            for key, value in headers.items():
                key = key.upper().replace('-', '_')
                if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                    key = f'HTTP_{key}'
                environ[key] = value
            
            # Add query parameters
            if event.get('queryStringParameters'):
                query_parts = []
                for key, value in event['queryStringParameters'].items():
                    query_parts.append(f"{key}={value}")
                environ['QUERY_STRING'] = '&'.join(query_parts)
            
            # Add body
            if event.get('body'):
                environ['wsgi.input'] = StringIO(event['body'])
                environ['CONTENT_LENGTH'] = str(len(event['body']))
            
            # Response container
            response_data = {}
            
            def start_response(status, headers):
                response_data['status'] = int(status.split()[0])
                response_data['headers'] = dict(headers)
            
            # Call Flask app
            response = app(environ, start_response)
            
            # Get response body
            response_body = b''.join(response).decode('utf-8')
            
            return {
                'statusCode': response_data.get('status', 200),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': response_body
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
