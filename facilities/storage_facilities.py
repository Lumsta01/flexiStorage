import json
import boto3
import os
from botocore.exceptions import ClientError


FACILITIES_TABLE = os.getenv('ACILITIES_TABLE', None)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(FACILITIES_TABLE)

"""Lambda handler: Routes requests to the appropriate function"""
def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['resource']

    if method == 'GET':
        if path == '/facilities':
            return get_all_facilities()
        elif path == '/facilities/search':
            query_params = event.get('queryStringParameters', {})
            return search_facilities(query_params)

    # Handle POST, PUT, DELETE later if needed
    return build_response(400, {'message': 'Invalid Request'})

"""Function to get all storage facilities (GET /facilities)"""
def get_all_facilities():
    try:
        response = table.scan()  # Fetch all facilities from DynamoDB
        facilities = response.get('Items', [])
        return build_response(200, facilities)
    except ClientError as e:
        return build_response(500, {'error': str(e)})

"""Function to search facilities based on parameters (GET /facilities/search)"""
def search_facilities(query_params):
    try:
        location = query_params.get('location')
        facility_type = query_params.get('type')

        # Dynamically build filter expression based on search params
        filter_expression = []
        expression_values = {}

        if location:
            filter_expression.append('location = :location')
            expression_values[':location'] = location

        if facility_type:
            filter_expression.append('type = :type')
            expression_values[':type'] = facility_type

        # Construct the filter expression
        filter_expression = " AND ".join(filter_expression) if filter_expression else None

        # Perform the scan with the filter expression
        response = table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_values
        )

        return build_response(200, response.get('Items', []))
    except ClientError as e:
        return build_response(500, {'error': str(e)})

"""Helper function to format API responses uniformly"""
def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'body': json.dumps(body)
    }
