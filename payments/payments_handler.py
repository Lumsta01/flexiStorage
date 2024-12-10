import json
import uuid
import os
import boto3
from botocore.exceptions import ClientError

# Get environment variables
payments_table = os.getenv('PAYMENTS_TABLE')
dynamodb = boto3.resource('dynamodb')
payments_table = dynamodb.Table(payments_table)

# For retrieving facility data if necessary
facilities_table = os.getenv('FACILITIES_TABLE')
facilities_table = dynamodb.Table(facilities_table)

def process_payment(event, context):
    """
    Handle a payment creation request.
    The function expects a POST body with payment details and stores it in DynamoDB.
    """
    try:
        body = json.loads(event['body'])
        facility_id = body['facility_id']
        amount = body['amount']
        payment_method = body['payment_method']  #  'credit_card', 'bank_transfer', etc.
        payment_status = 'Pending'  # For simplicity, assuming pending payments

        # Validate that the facility exists in the Facilities table
        facility_response = facilities_table.get_item(Key={'facility_id': facility_id})
        if 'Item' not in facility_response:
            return create_response(400, {'message': 'Facility not found'})

        # Generate a unique payment ID
        payment_id = str(uuid.uuid4())

        # Store the payment in the Payments table
        payment_item = {
            'payment_id': payment_id,
            'facility_id': facility_id,
            'amount': amount,
            'payment_method': payment_method,
            'payment_status': payment_status,
            'created_at': str(event['requestContext']['requestTime'])  # Use request time as timestamp
        }

        payments_table.put_item(Item=payment_item)

        return create_response(201, {'message': 'Payment created successfully', 'payment_id': payment_id})

    except ClientError as e:
        return create_response(500, {'error': f'Error processing payment: {str(e)}'})
    except KeyError as e:
        return create_response(400, {'error': f'Missing required field: {str(e)}'})

def get_payments(event, context):
    """
    Retrieve all payments or payments related to a specific facility.
    This function handles GET requests for listing payments.
    """
    try:
        facility_id = event.get('queryStringParameters', {}).get('facility_id')

        # If facility_id is provided, query payments for that facility
        if facility_id:
            response = payments_table.query(
                IndexName='FacilityIdIndex',
                KeyConditionExpression='facility_id = :facility_id',
                ExpressionAttributeValues={':facility_id': facility_id}
            )
            payments = response.get('Items', [])
        else:
            # If no facility_id is provided, retrieve all payments (could be paginated if needed)
            response = payments_table.scan()
            payments = response.get('Items', [])

        return create_response(200, payments)

    except ClientError as e:
        return create_response(500, {'error': f'Error retrieving payments: {str(e)}'})

def create_response(status_code, body):
    """Helper function to create a response with proper headers."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }
