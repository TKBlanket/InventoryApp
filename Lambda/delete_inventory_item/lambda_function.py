import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Inventory')

    # Extract the '_id' from the path parameters
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    key_value = event['pathParameters']['id']

    try:
        # Extract item id from path parameters
        item_id = event['pathParameters']['id']
        
        # First, we need to query to get all items with this id (across all locations)
        # Since id is the partition key, we can query the main table
        response = table.query(
            KeyConditionExpression=Key('id').eq(item_id)
        )
        items = response.get('Items', [])
        
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found')
            }

        for item in items:
            table.delete_item(
                Key={
                    'id': item['id'],
                    'location_id': item['location_id']
                }
            )

        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully deleted {item_id} item')
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error deleting item: {str(e)}")
        }