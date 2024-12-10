import json
import uuid
import os
import boto3
from botocore.exceptions import ClientError

# Get environment variables
payments_table_name = os.getenv('PAYMENTS_TABLE')
dynamodb = boto3.resource('dynamodb')
payments_table = dynamodb.Table(payments_table_name)

# For retrieving facility data if necessary
facilities_table_name = os.getenv('FACILITIES_TABLE')
facilities_table = dynamodb.Table(facilities_table_name)

def process_payment(event, context):
    try:
        body = json.loads(event['body'])
        facility_id = body['facility_id']
        amount = body['payment_amount']  # Amount is now coming from the front-end
        payment_method = body['payment_type']  # Payment method (credit card, PayPal, etc.)
        start_date = body['start_date']
        end_date = body['end_date']

        # Generate unique payment ID
        payment_id = str(uuid.uuid4())

        # Validate that the facility exists in the Facilities table (this can be an optional step)
        facility_response = facilities_table.get_item(Key={'facility_id': facility_id})
        if 'Item' not in facility_response:
            return create_response(400, {'message': 'Facility not found'})

        # Store payment data in DynamoDB
        payment_item = {
            'payment_id': payment_id,
            'facility_id': facility_id,
            'user_id': body['user_id'],  # Ensure user_id is also passed
            'amount': amount,
            'payment_method': payment_method,
            'payment_status': 'Pending',  # Mark as Pending until confirmed
            'start_date': start_date,
            'end_date': end_date,
            'created_at': str(event['requestContext']['requestTime'])  # Timestamp
        }

        # Insert the payment record into the payments table
        payments_table.put_item(Item=payment_item)

        # Simulate payment gateway processing (replace with actual payment processing code)
        payment_gateway_response = simulate_payment_gateway(amount, payment_method)

        # Update payment status to 'Completed' after payment is successfully processed
        if payment_gateway_response['status'] == 'success':
            update_response = payments_table.update_item(
                Key={'payment_id': payment_id},
                UpdateExpression="SET payment_status = :status, transaction_id = :transaction_id",
                ExpressionAttributeValues={
                    ':status': 'Completed',
                    ':transaction_id': payment_gateway_response['transaction_id']
                },
                ReturnValues="ALL_NEW"
            )

            return create_response(200, {
                'message': 'Payment processed successfully',
                'payment_id': payment_id,
                'payment_status': 'Completed',
                'transaction_id': update_response['Attributes']['transaction_id']
            })
        else:
            return create_response(400, {'message': 'Payment failed', 'error': payment_gateway_response['error_message']})

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
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Credentials': 'false'
        },
        'body': json.dumps(body)
    }
