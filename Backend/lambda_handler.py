import json
from app import app

def handler(event, context):
    """AWS Lambda handler for Flask app"""
    try:
        # Handle HTTP API Gateway v2.0 format
        if 'requestContext' in event and 'http' in event['requestContext']:
            # HTTP API v2.0 format
            method = event['requestContext']['http']['method']
            path = event.get('rawPath', '/')
            query_string = event.get('rawQueryString', '')
            headers = event.get('headers', {})
            body = event.get('body', '')
        else:
            # REST API v1.0 format (fallback)
            method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
            query_string = ''
            if event.get('queryStringParameters'):
                query_parts = []
                for key, value in event['queryStringParameters'].items():
                    query_parts.append(f"{key}={value}")
                query_string = '&'.join(query_parts)
            headers = event.get('headers', {})
            body = event.get('body', '')

        # Create WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', ''),
            'CONTENT_LENGTH': str(len(body)) if body else '0',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '443',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': None,
            'wsgi.errors': None,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False
        }

        # Add headers to environ
        for key, value in headers.items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                key = f'HTTP_{key}'
            environ[key] = value

        # Add body
        if body:
            from io import StringIO
            environ['wsgi.input'] = StringIO(body)

        # Response container
        response_data = {'status': 200, 'headers': {}}

        def start_response(status, response_headers):
            response_data['status'] = int(status.split()[0])
            response_data['headers'] = dict(response_headers)

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
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e), 'type': type(e).__name__})
        }
