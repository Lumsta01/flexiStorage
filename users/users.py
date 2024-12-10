import json
import uuid
import os
import boto3
from datetime import datetime

# DynamoDB Table Setup
USERS_TABLE = os.getenv('USERS_TABLE', None)
dynamodb = boto3.resource('dynamodb')
ddbTable = dynamodb.Table(USERS_TABLE)

# Cognito Setup
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID', None)
COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID', None)
cognito_client = boto3.client('cognito-idp')

# Helper Functions


def create_cors_response(status_code, body):
    """Create a response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Credentials': 'false'
        },
        'body': json.dumps(body) if body else ''
    }

"""Gets all the users"""
def get_all_users(event):
    ddb_response = ddbTable.scan(Select='ALL_ATTRIBUTES')
    return ddb_response.get('Items', []), 200

"""Gets a specific user"""
def get_user_by_id(event):
    userid = event['pathParameters']['userid']
    ddb_response = ddbTable.get_item(Key={'userid': userid})
    return ddb_response.get('Item', {}), 200

"""Creates a new user"""
def create_user(event):
    request_json = json.loads(event['body'])
    email = request_json['email']
    password = request_json.get('password', 'Temp@1234')  # Default temp password
    timestamp = datetime.now().isoformat()
    userid = request_json.get('userid', str(uuid.uuid1()))

    # Register user in Cognito
    try:
        cognito_client.admin_create_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=email,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'false'}
            ],
            TemporaryPassword=password,
            MessageAction='SUPPRESS'
        )
    except cognito_client.exceptions.UsernameExistsException:
        return create_cors_response(400, {"Message": "User already exists."})
    except cognito_client.exceptions.InvalidParameterException as e:
        return create_cors_response(400, {"Message": f"Invalid parameters: {str(e)}"})
    except Exception as e:
        return create_cors_response(500, {"Message": f"Error creating user in Cognito: {str(e)}"})

    # Save user data to DynamoDB
    try:
        request_json.update({
            'timestamp': timestamp,
            'userid': userid
        })
        ddbTable.put_item(Item=request_json)
    except Exception as e:
        return create_cors_response(500, {"Message": f"Error saving user to DynamoDB: {str(e)}"})

    return create_cors_response(201, request_json)


"""Edits a specific user info"""
def update_user(event):
    userid = event['pathParameters']['userid']
    request_json = json.loads(event['body'])
    request_json['timestamp'] = datetime.now().isoformat()
    request_json['userid'] = userid
    ddbTable.put_item(Item=request_json)
    return request_json, 200

"""Deletes a specific user"""
def delete_user(event):
    userid = event['pathParameters']['userid']
    ddbTable.delete_item(Key={'userid': userid})
    return {}, 204

"""invalid request"""
def unsupported_route(event):
    return {'Message': 'Unsupported route'}, 400

# Route Mapping
ROUTES = {
    'GET /users': get_all_users,
    'GET /users/{userid}': get_user_by_id,
    'POST /users': create_user,
    'PUT /users/{userid}': update_user,
    'DELETE /users/{userid}': delete_user
}

def lambda_handler(event, context):
    route_key = f"{event['httpMethod']} {event['resource']}"
    handler_function = ROUTES.get(route_key, unsupported_route)
    
    try:
        # Call the handler function
        response_body, status_code = handler_function(event)
    except Exception as err:
        # Handle exceptions
        response_body, status_code = {'Error': str(err)}, 500

    # Return the response with CORS headers
    return create_cors_response(status_code, response_body)

