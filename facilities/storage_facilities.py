import json
import boto3
import os
import base64
from botocore.exceptions import ClientError
import uuid
import decimal

FACILITIES_TABLE = os.getenv('FACILITIES_TABLE', None)  # Ensure your environment variable name is correct
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', None)  # Ensure your environment variable for S3 bucket name is set

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
    
    if method == 'POST' and path == '/facilities':
        return add_facility(event)

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

"""Function to add a new facility (POST /facilities)"""
def add_facility(event):
    try:
        # Parse the request body
        body = json.loads(event['body'])
        facility_name = body['facility_name']
        location = body['location']
        facility_type = body['type']
        image_data = body['image']  # Assuming base64 image data
        capacity = body['capacity']  # Ensure capacity is passed in the request
        description = body.get('description', '')  # Add description (default to empty string if not provided)

        # Save the image to S3 and get the URL
        image_url = save_image_to_s3(image_data, facility_name)

        # Generate a unique facility_id (UUID, for example)
        facility_id = str(uuid.uuid4())

        # Store the facility details in DynamoDB
        table.put_item(
            Item={
                'facility_id': facility_id,
                'facility_name': facility_name,
                'location': location,
                'type': facility_type,
                'image_url': image_url,
                'capacity': capacity,
                'description': description 
            }
        )

        return build_response(201, {'message': 'Facility added successfully!'})

    except ClientError as e:
        return build_response(500, {'error': str(e)})
    
def delete_facility(facility_id):
    try:
        # Delete the facility from DynamoDB by facility_id
        response = table.delete_item(
            Key={'facility_id': facility_id}
        )

        # Check if the item was deleted successfully (a successful deletion returns a response without an error)
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
            return build_response(200, {'message': 'Facility deleted successfully!'})
        else:
            return build_response(404, {'message': 'Facility not found'})

    except ClientError as e:
        return build_response(500, {'error': str(e)})


"""Helper function to save the image to S3 and return the URL"""
def save_image_to_s3(image_data, facility_name):
    # Convert base64 to binary data (if needed)
    image_binary = base64.b64decode(image_data)
    
    # Generate a unique image file name (e.g., facility_name + UUID)
    image_filename = f"{facility_name}-{str(uuid.uuid4())}.jpg"
    
    # Upload to S3
    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=image_filename,
        Body=image_binary,
        ContentType='image/jpeg'
    )
    
    # Return the URL of the uploaded image
    image_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{image_filename}"
    return image_url

"""Helper function to build API responses uniformly"""
def build_response(status_code, body):
    body = convert_decimal(body) 
    return {
        'statusCode': status_code,
        'body': json.dumps(body)
    }
