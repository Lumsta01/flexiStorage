import json
import boto3
import os
import base64
from botocore.exceptions import ClientError
import uuid
import decimal

FACILITIES_TABLE = os.getenv('FACILITIES_TABLE', None)
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', None)

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table(FACILITIES_TABLE)

def convert_decimal(obj):
    """Convert Decimal objects to float."""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal(item) for item in obj]
    else:
        return obj

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
        'body': json.dumps(convert_decimal(body)) if body else ''
    }
    

def lambda_handler(event, context):
    # Handle OPTIONS requests for CORS preflight
    if event['httpMethod'] == 'OPTIONS':
        return create_cors_response(200, None)

    method = event['httpMethod']
    path = event['resource']

    try:
        if method == 'GET':
            if path == '/facilities':
                return get_all_facilities()
            elif path == '/facilities/search':
                query_params = event.get('queryStringParameters', {})
                return search_facilities(query_params)
        elif method == 'POST' and path == '/facilities':
            return add_facility(event)
        elif method == 'DELETE' and path == '/facilities/{facility_id}':
            facility_id = event['pathParameters']['facility_id']
            return delete_facility(facility_id)
        
        return create_cors_response(400, {'message': 'Invalid Request'})
    except Exception as e:
        return create_cors_response(500, {'error': str(e)})

def get_all_facilities():
    try:
        response = table.scan()
        facilities = response.get('Items', [])
        return create_cors_response(200, facilities)
    except ClientError as e:
        return create_cors_response(500, {'error': str(e)})

def search_facilities(query_params):
    try:
        location = query_params.get('location')
        facility_type = query_params.get('type')

        filter_expression = []
        expression_values = {}

        if location:
            filter_expression.append('location = :location')
            expression_values[':location'] = location

        if facility_type:
            filter_expression.append('#type = :type')
            expression_values[':type'] = facility_type

        filter_expression = " AND ".join(filter_expression) if filter_expression else None

        scan_params = {}
        if filter_expression:
            scan_params['FilterExpression'] = filter_expression
            scan_params['ExpressionAttributeValues'] = expression_values
            if facility_type:  # Add ExpressionAttributeNames only if type is used
                scan_params['ExpressionAttributeNames'] = {'#type': 'type'}

        response = table.scan(**scan_params)
        return create_cors_response(200, response.get('Items', []))
    except ClientError as e:
        return create_cors_response(500, {'error': str(e)})

def add_facility(event):
    try:
        body = json.loads(event['body'])
        facility_name = body['facility_name']
        location = body['location']
        facility_type = body['type']
        image_data = body['image']
        capacity = body['capacity']
        price = body['price']  # Add this line
        description = body.get('description', '')

        image_url = save_image_to_s3(image_data, facility_name)
        facility_id = str(uuid.uuid4())

        table.put_item(
            Item={
                'facility_id': facility_id,
                'facility_name': facility_name,
                'location': location,
                'type': facility_type,
                'image_url': image_url,
                'capacity': capacity,
                'price': price,
                'description': description 
            }
        )

        return create_cors_response(201, {'message': 'Facility added successfully!', 'facility_id': facility_id})
    except ClientError as e:
        return create_cors_response(500, {'error': str(e)})
    except KeyError as e:
        return create_cors_response(400, {'error': f'Missing required field: {str(e)}'})

def delete_facility(facility_id):
    try:
        response = table.delete_item(
            Key={'facility_id': facility_id},
            ReturnValues='ALL_OLD'
        )
        
        if 'Attributes' in response:
            return create_cors_response(200, {'message': 'Facility deleted successfully!'})
        else:
            return create_cors_response(404, {'message': 'Facility not found'})
    except ClientError as e:
        return create_cors_response(500, {'error': str(e)})

def save_image_to_s3(image_data, facility_name):
    try:
        image_binary = base64.b64decode(image_data)
        image_filename = f"{facility_name}-{str(uuid.uuid4())}.jpg"
        
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=image_filename,
            Body=image_binary,
            ContentType='image/jpeg'
        )
        
        image_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{image_filename}"
        return image_url
    except Exception as e:
        raise Exception(f"Error saving image to S3: {str(e)}")