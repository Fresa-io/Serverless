import os
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
    try:
        # Validate trigger source
        if event['triggerSource'] != 'CreateAuthChallenge_Authentication':
            raise ValueError(f"Invalid trigger source: {event['triggerSource']}")

        # Get email from user attributes
        user_attributes = event['request']['userAttributes']
        email = user_attributes.get('email', '').lower()
        
        if not email:
            raise ValueError("Email not found in user attributes")
        
        # Retrieve code from DynamoDB
        item = table.get_item(Key={'email': email}).get('Item', {})
        code = item.get('code', '')
        
        if not code:
            raise ValueError(f"No code found for {email}")
        
        # Build Cognito response
        event['response'] = {
            'publicChallengeParameters': {'email': email},
            'privateChallengeParameters': {'code': code},
            'challengeMetadata': 'OTP-REQUIRED'
        }
        event['version'] = 1
        
        return event

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'response': {
                'publicChallengeParameters': {},
                'privateChallengeParameters': {},
                'challengeMetadata': 'ERROR'
            },
            'version': 1
        }