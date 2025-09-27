import os
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB lazily to avoid issues during testing
_dynamodb = None
_table = None


def get_dynamodb_resource():
    """Get DynamoDB resource with lazy initialization"""
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb")
    return _dynamodb


def get_table():
    """Get DynamoDB table with lazy initialization"""
    global _table
    if _table is None:
        dynamodb = get_dynamodb_resource()
        _table = dynamodb.Table(os.environ["DYNAMODB_TABLE_NAME"])
    return _table


def lambda_handler(event, context):
    try:
        # Validate trigger source
        if event["triggerSource"] != "CreateAuthChallenge_Authentication":
            raise ValueError(f"Invalid trigger source: {event['triggerSource']}")

        # Get email from user attributes
        user_attributes = event["request"]["userAttributes"]
        email = user_attributes.get("email", "").lower()

        if not email:
            raise ValueError("Email not found in user attributes")

        # Retrieve code from DynamoDB
        table = get_table()
        item = table.get_item(Key={"email": email}).get("Item", {})
        code = item.get("code", "")

        if not code:
            raise ValueError(f"No code found for {email}")

        # Build Cognito response
        event["response"] = {
            "publicChallengeParameters": {"email": email},
            "privateChallengeParameters": {"code": code},
            "challengeMetadata": "OTP-REQUIRED",
        }
        event["version"] = 1

        return event

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            "response": {
                "publicChallengeParameters": {},
                "privateChallengeParameters": {},
                "challengeMetadata": "ERROR",
            },
            "version": 1,
        }
