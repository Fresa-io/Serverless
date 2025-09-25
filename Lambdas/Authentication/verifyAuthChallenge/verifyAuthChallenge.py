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


def get_dynamodb_resource():
    """Get DynamoDB resource with lazy initialization"""
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb")
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
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        response = table.get_item(Key={"email": email})

        # Check if code record doesn't exist (deleted or never created)
        if "Item" not in response:
            return {
                "valid": False,
                "error": "Verification code has expired",
                "status_code": 401,
            }

        item = response["Item"]
        stored_code = item.get("code")
        last_request_time = item.get("lastRequestTime")  # Unix timestamp

        # Check if code has expired based on time
        if last_request_time:
            current_time = int(time.time())
            expiration_time = last_request_time + (CODE_EXPIRATION_MINUTES * 60)

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
    try:
        # Parse JSON body safely
        try:
            body = json.loads(event["body"])
        except JSONDecodeError as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid JSON: {str(e)}"}),
            }

        email = body.get("email", "").lower().strip()
        code = body.get("code", "")

        # Validate required fields
        if not email or not code:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing email or code"}),
            }

        # First, check if user exists in Cognito
        try:
            user_exists_in_cognito = check_user_exists_in_cognito(email)
        except ClientError as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Error checking user existence"}),
            }

        if not user_exists_in_cognito:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "User does not exist"}),
            }

        # User exists in Cognito, now validate the code against DynamoDB
        code_validation = validate_code_in_dynamodb(email, code)
        if not code_validation["valid"]:
            return {
                "statusCode": code_validation["status_code"],
                "body": json.dumps({"error": code_validation["error"]}),
            }

        # User exists and code is valid, proceed with custom auth flow
        try:
            auth_response = cognito.initiate_auth(
                ClientId=CLIENT_ID,
                AuthFlow="CUSTOM_AUTH",
                AuthParameters={"USERNAME": email},
            )

            # Respond to challenge
            challenge_response = cognito.respond_to_auth_challenge(
                ClientId=CLIENT_ID,
                ChallengeName="CUSTOM_CHALLENGE",
                Session=auth_response["Session"],
                ChallengeResponses={"USERNAME": email, "ANSWER": code},
            )

            # Extract all available token information
            auth_result = challenge_response["AuthenticationResult"]

            response_data = {
                "access_token": auth_result["AccessToken"],
                "id_token": auth_result["IdToken"],
                "token_type": auth_result.get("TokenType", "Bearer"),
                "expires_in": auth_result.get("ExpiresIn"),
            }

            # Add refresh token if available (may not be present in custom auth flow)
            if "RefreshToken" in auth_result:
                response_data["refresh_token"] = auth_result["RefreshToken"]

            return {"statusCode": 200, "body": json.dumps(response_data)}

        except ClientError as e:
            error_code = e.response["Error"].get("Code")

            # Handle various Cognito-specific exceptions
            if error_code == "NotAuthorizedException":
                return {
                    "statusCode": 401,
                    "body": json.dumps(
                        {"error": "Invalid code or authentication failed"}
                    ),
                }
            elif error_code == "CodeMismatchException":
                return {
                    "statusCode": 401,
                    "body": json.dumps({"error": "Invalid verification code"}),
                }
            elif error_code == "ExpiredCodeException":
                return {
                    "statusCode": 401,
                    "body": json.dumps({"error": "Verification code has expired"}),
                }
            elif error_code == "InvalidLambdaResponseException":
                return {
                    "statusCode": 500,
                    "body": json.dumps(
                        {"error": "Authentication service configuration error"}
                    ),
                }
            else:
                return {
                    "statusCode": 401,
                    "body": json.dumps({"error": f"Authentication failed: {str(e)}"}),
                }

    except Exception as e:
        # Fallback for all other exceptions
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }
