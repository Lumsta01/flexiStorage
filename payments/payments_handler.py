import json
import os
import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime

# Environment Variables
PAYMENTS_TABLE = os.getenv('PAYMENTS_TABLE', None)
dynamodb = boto3.resource('dynamodb')
payments_table = dynamodb.Table(PAYMENTS_TABLE)

# Helper function to create CORS responses
def create_cors_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Amz-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Credentials': 'false'
        },
        'body': json.dumps(body) if body else ''
    }

# Lambda Handler function
def lambda_handler(event, context):
    try:
        method = event['httpMethod']
        path = event['resource']
        
        if method == 'OPTIONS':
            return create_cors_response(200, None)

        # Handle POST request for creating a payment
        if method == 'POST' and path == '/payments':
            return create_payment(event)
        
        # Handle GET request to fetch all payments
        elif method == 'GET' and path == '/payments':
            return get_payments()
        
        # Handle DELETE request for canceling a specific payment by payment_id
        elif method == 'DELETE' and '/payments/' in path:
            payment_id = event['pathParameters']['payment_id']
            return cancel_payment(payment_id)
        
        # If none of the above, return an error response
        else:
            return create_cors_response(400, {'message': 'Invalid Request'})
    
    except Exception as e:
        return create_cors_response(500, {'error': str(e)})

# Function to create a new payment
def create_payment(event):
    try:
        # Parse the request body to get payment details
        body = json.loads(event['body'])
        facility_id = body['facility_id']
        booking_id = body['booking_id']
        payment_amount = body['payment_amount']
        payment_type = body['payment_type']
        payment_status = body.get('payment_status', 'Pending')  # Default to 'Pending'
        
        # Generate a unique payment ID
        payment_id = str(uuid.uuid4())

        # Store the payment in the DynamoDB table
        payments_table.put_item(
            Item={
                'payment_id': payment_id,
                'facility_id': facility_id,
                'booking_id': booking_id,
                'payment_amount': payment_amount,
                'payment_type': payment_type,
                'payment_status': payment_status,
                'created_at': datetime.now().isoformat()  # Include creation timestamp
            }
        )
        
        # Return a success response with the payment ID
        return create_cors_response(201, {'message': 'Payment created successfully!', 'payment_id': payment_id})
    
    except KeyError as e:
        return create_cors_response(400, {'error': f'Missing required field: {str(e)}'})
    
    except ClientError as e:
        return create_cors_response(500, {'error': str(e)})

# Function to get all payments
def get_payments():
    try:
        # Scan the payments table and retrieve all payments
        response = payments_table.scan()
        return create_cors_response(200, response.get('Items', []))
    
    except ClientError as e:
        return create_cors_response(500, {'error': str(e)})

# Function to cancel a payment by payment_id
def cancel_payment(payment_id):
    try:
        # Update the status of the payment to "Cancelled"
        response = payments_table.update_item(
            Key={'payment_id': payment_id},
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={'#status': 'payment_status'},
            ExpressionAttributeValues={':status': 'Cancelled'},
            ReturnValues="ALL_NEW"
        )
        
        # Return a success response with the updated payment details
        return create_cors_response(200, {'message': 'Payment cancelled successfully!', 'payment': response.get('Attributes')})
    
    except ClientError as e:
        return create_cors_response(500, {'error': str(e)})
