import json
from app import app
from werkzeug.serving import WSGIRequestHandler

def handler(event, context):
    """AWS Lambda handler for Flask app"""
    try:
        # Handle API Gateway event
        if 'httpMethod' in event:
            from werkzeug.wrappers import Request
            from werkzeug.test import EnvironBuilder
            
            # Build WSGI environ from API Gateway event
            builder = EnvironBuilder(
                path=event.get('path', '/'),
                method=event.get('httpMethod', 'GET'),
                headers=event.get('headers', {}),
                data=event.get('body', ''),
                query_string=event.get('queryStringParameters') or {}
            )
            
            environ = builder.get_environ()
            
            # Handle the request
            response = app(environ, lambda status, headers: None)
            
            # Convert response to API Gateway format
            response_body = b''.join(response).decode('utf-8')
            
            return {
                'statusCode': 200,
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
