import boto3
import json
import os
import time
from json import JSONDecodeError
from botocore.exceptions import ClientError

# Initialize AWS services lazily to avoid issues during testing
_cognito = None
_dynamodb = None


def get_cognito_client():
    """Get Cognito client with lazy initialization"""
    global _cognito
    if _cognito is None:
        _cognito = boto3.client("cognito-idp")
    return _cognito


def get_dynamodb_client():
    """Get DynamoDB client with lazy initialization"""
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.client("dynamodb")
    return _dynamodb


# Lazy loading of environment variables to avoid KeyError during testing
def get_client_id():
    return os.environ["COGNITO_CLIENT_ID"]


def get_user_pool_id():
    return os.environ["COGNITO_USER_POOL_ID"]


def get_dynamodb_table_name():
    return os.environ["DYNAMODB_TABLE_NAME"]


def get_code_expiration_minutes():
    return int(os.environ.get("CODE_EXPIRATION_MINUTES", "5"))


def check_user_exists_in_cognito(email):
    """Check if user exists in Cognito"""
    try:
        cognito = get_cognito_client()
        cognito.admin_get_user(UserPoolId=get_user_pool_id(), Username=email)
        return True
    except ClientError as e:
        if e.response["Error"].get("Code") == "UserNotFoundException":
            return False
        else:
            # Re-raise other errors
            raise


def validate_code_in_dynamodb(email, code):
    """Validate the code against DynamoDB and return validation result"""
    try:
        dynamodb = get_dynamodb_client()
        table_name = get_dynamodb_table_name()
        response = dynamodb.get_item(TableName=table_name, Key={"email": {"S": email}})

        # Check if code record doesn't exist (deleted or never created)
        if "Item" not in response:
            return {
                "valid": False,
                "error": "Verification code has expired",
                "status_code": 401,
            }

        item = response["Item"]
        stored_code = item.get("code", {}).get("S")  # DynamoDB client format
        last_request_time = item.get("lastRequestTime", {}).get("N")  # Unix timestamp as string
        if last_request_time:
            last_request_time = int(last_request_time)

        # Check if code has expired based on time
        if last_request_time:
            current_time = int(time.time())
            expiration_time = last_request_time + (get_code_expiration_minutes() * 60)

            if current_time > expiration_time:
                return {
                    "valid": False,
                    "error": "Verification code has expired",
                    "status_code": 401,
                }

        # Check if code matches
        if stored_code != code:
            return {"valid": False, "error": "Invalid code", "status_code": 401}

        return {"valid": True}

    except ClientError as dynamodb_error:
        return {"valid": False, "error": "Database error occurred", "status_code": 500}


def lambda_handler(event, context):
    """
    Lambda handler for Cognito custom auth challenge verification
    """
    try:
        print(f"🔍 verifyAuthChallenge started - Request ID: {context.aws_request_id}")
        print(f"📝 Event received: {json.dumps(event)}")

        # Extract challenge answer from the event
        challenge_answer = event.get("request", {}).get("challengeAnswer", "")
        user_attributes = event.get("request", {}).get("userAttributes", {})
        email = user_attributes.get("email", "")

        if not challenge_answer or not email:
            print("❌ Missing challenge answer or email")
            return {
                "answerCorrect": False
            }

        print(f"🔍 Verifying challenge for email: {email}")
        print(f"🔍 Challenge answer: {challenge_answer}")

        # Validate the code against DynamoDB
        code_validation = validate_code_in_dynamodb(email, challenge_answer)
        print(f"✅ Code validation result: {code_validation}")

        if not code_validation["valid"]:
            print(f"❌ Code validation failed: {code_validation['error']}")
            return {
                "answerCorrect": False
            }

        print(f"✅ Challenge verification successful for: {email}")
        # Ensure the response is exactly what Cognito expects
        response = {
            "answerCorrect": True
        }
        print(f"🔍 Returning response: {response}")
        print(f"🔍 Response type: {type(response)}")
        print(f"🔍 Response keys: {list(response.keys())}")
        print(f"🔍 Response answerCorrect value: {response['answerCorrect']}")
        print(f"🔍 Response answerCorrect type: {type(response['answerCorrect'])}")
        return response

    except Exception as e:
        print(f"❌ Error in verifyAuthChallenge: {str(e)}")
        response = {
            "answerCorrect": False
        }
        print(f"🔍 Returning error response: {response}")
        return response
