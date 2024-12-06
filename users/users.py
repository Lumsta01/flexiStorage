import json
import uuid
import os
import boto3
from datetime import datetime

# DynamoDB Table Setup
USERS_TABLE = os.getenv('USERS_TABLE', None)
dynamodb = boto3.resource('dynamodb')
ddbTable = dynamodb.Table(USERS_TABLE)

# Helper Functions

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
    request_json['timestamp'] = datetime.now().isoformat()
    request_json['userid'] = request_json.get('userid', str(uuid.uuid1()))
    ddbTable.put_item(Item=request_json)
    return request_json, 201


"""Edits a specific user info"""
def update_user(event):
    userid = event['pathParameters']['userid']
    request_json = json.loads(event['body'])
    request_json['timestamp'] = datetime.now().isoformat()
    request_json['userid'] = userid
    ddbTable.put_item(Item=request_json)
    return request_json, 200

"""Deletes a specific usse"""
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
        response_body, status_code = handler_function(event)
    except Exception as err:
        response_body, status_code = {'Error': str(err)}, 500
    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
