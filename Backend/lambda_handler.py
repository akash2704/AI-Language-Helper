import json
import sys
import os
from io import StringIO

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def handler(event, context):
    """AWS Lambda handler for Flask app"""
    try:
        from app import app
        
        # Extract request info from event
        if 'requestContext' in event and 'http' in event['requestContext']:
            # HTTP API v2.0 format
            method = event['requestContext']['http']['method']
            path = event.get('rawPath', '/')
            query_string = event.get('rawQueryString', '')
            headers = event.get('headers', {})
            body = event.get('body', '')
        else:
            # REST API v1.0 format
            method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
            query_string = ''
            if event.get('queryStringParameters'):
                params = []
                for k, v in event['queryStringParameters'].items():
                    params.append(f"{k}={v}")
                query_string = '&'.join(params)
            headers = event.get('headers', {})
            body = event.get('body', '')

        # Handle preflight CORS
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': ''
            }

        # Create WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', 'application/json'),
            'CONTENT_LENGTH': str(len(body or '')),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '443',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': StringIO(body or ''),
            'wsgi.errors': StringIO(),
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False
        }

        # Add headers
        for key, value in headers.items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                key = f'HTTP_{key}'
            environ[key] = value

        # Response data
        response_data = {'status': 200, 'headers': []}

        def start_response(status, response_headers):
            response_data['status'] = int(status.split()[0])
            response_data['headers'] = response_headers

        # Call Flask app
        response_iter = app(environ, start_response)
        response_body = b''.join(response_iter).decode('utf-8')

        return {
            'statusCode': response_data['status'],
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': response_body
        }

    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        }
