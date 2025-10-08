import boto3
import json
import os
import time
import signal
from json import JSONDecodeError
from botocore.exceptions import ClientError

# Initialize clients lazily to avoid region issues during testing
_cognito = None
_dynamodb = None


def get_cognito_client():
    global _cognito
    if _cognito is None:
        _cognito = boto3.client("cognito-idp")
    return _cognito


def get_dynamodb_client():
    """Get DynamoDB client with retry configuration"""
    global _dynamodb
    if _dynamodb is None:
        # Use client instead of resource for better control
        region = os.environ.get("AWS_REGION", "us-east-1")
        print(f"🔍 Creating DynamoDB client in region: {region}")
        from botocore.config import Config

        config = Config(
            retries={"max_attempts": 3, "mode": "adaptive"},
            connect_timeout=10,
            read_timeout=10,
        )
        _dynamodb = boto3.client("dynamodb", region_name=region, config=config)
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
    """Check if user exists in Cognito..."""
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
        print(f"🔍 Getting DynamoDB client...")
        dynamodb = get_dynamodb_client()
        table_name = get_dynamodb_table_name()
        print(f"🔍 Accessing table: {table_name}")
        print(f"🔍 Querying DynamoDB for email: {email}")

        # Use client.get_item with explicit timeout and error handling
        try:
            response = dynamodb.get_item(TableName=table_name, Key={"email": {"S": email}})
            print(f"✅ DynamoDB response received: {response}")
        except Exception as dynamodb_error:
            print(f"❌ DynamoDB query error: {str(dynamodb_error)}")
            return {"valid": False, "error": "Database connection error", "status_code": 500}

        # Check if code record doesn't exist (deleted or never created)
        if "Item" not in response:
            return {
                "valid": False,
                "error": "Verification code has expired",
                "status_code": 401,
            }

        item = response["Item"]
        stored_code = item.get("code", {}).get("S")  # DynamoDB client format
        last_request_time = item.get("lastRequestTime", {}).get(
            "N"
        )  # Unix timestamp as string
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
        print(f"❌ DynamoDB ClientError: {str(dynamodb_error)}")
        return {"valid": False, "error": "Database error occurred", "status_code": 500}
    except Exception as e:
        print(f"❌ Unexpected error in DynamoDB validation: {str(e)}")
        return {"valid": False, "error": "Database error occurred", "status_code": 500}


def lambda_handler(event, context):
    try:
        print(f"🔍 Lambda started - Request ID: {context.aws_request_id}")
        
        # Set up timeout handler
        def timeout_handler(signum, frame):
            print(f"⏰ Lambda timeout - Request ID: {context.aws_request_id}")
            raise TimeoutError("Lambda function timeout")
        
        # Set timeout to 25 seconds (less than Lambda timeout)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(25)

        # Parse JSON body safely
        try:
            body = json.loads(event["body"])
            print(f"📝 Parsed request body: {body}")
        except JSONDecodeError as e:
            print(f"❌ JSON parse error: {str(e)}")
            signal.alarm(0)  # Cancel timeout
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid JSON: {str(e)}"}),
            }

        email = body.get("email", "").lower().strip()
        code = body.get("code", "")

        # Validate required fields
        if not email or not code:
            signal.alarm(0)  # Cancel timeout
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing email or code"}),
            }

        # First, check if user exists in Cognito
        print(f"🔍 Checking if user exists in Cognito: {email}")
        try:
            user_exists_in_cognito = check_user_exists_in_cognito(email)
            print(f"✅ User exists check result: {user_exists_in_cognito}")
        except ClientError as e:
            print(f"❌ Error checking user existence: {str(e)}")
            signal.alarm(0)  # Cancel timeout
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Error checking user existence"}),
            }

        if not user_exists_in_cognito:
            signal.alarm(0)  # Cancel timeout
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "User does not exist"}),
            }

        # User exists in Cognito, now validate the code against DynamoDB
        print(f"🔍 Validating code in DynamoDB for: {email}")
        code_validation = validate_code_in_dynamodb(email, code)
        print(f"✅ Code validation result: {code_validation}")
        if not code_validation["valid"]:
            signal.alarm(0)  # Cancel timeout
            return {
                "statusCode": code_validation["status_code"],
                "body": json.dumps({"error": code_validation["error"]}),
            }

        # User exists and code is valid, proceed with custom auth flow
        print(f"🔍 Starting Cognito custom auth flow for: {email}")
        try:
            cognito = get_cognito_client()
            print(f"🔍 Initiating auth with client ID: {get_client_id()}")
            auth_response = cognito.initiate_auth(
                ClientId=get_client_id(),
                AuthFlow="CUSTOM_AUTH",
                AuthParameters={"USERNAME": email},
            )
            print(
                f"✅ Auth initiated, session: {auth_response.get('Session', 'No session')}"
            )

            # Respond to challenge
            print(f"🔍 Responding to auth challenge with code: {code}")
            try:
                challenge_response = cognito.respond_to_auth_challenge(
                    ClientId=get_client_id(),
                    ChallengeName="CUSTOM_CHALLENGE",
                    Session=auth_response["Session"],
                    ChallengeResponses={"USERNAME": email, "ANSWER": code},
                )
                print(f"✅ Challenge response received: {challenge_response}")
            except Exception as challenge_error:
                print(f"❌ Challenge response error: {str(challenge_error)}")
                signal.alarm(0)  # Cancel timeout
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": f"Challenge response failed: {str(challenge_error)}"}),
                }

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

            print(f"✅ Authentication successful, returning tokens")
            signal.alarm(0)  # Cancel timeout
            return {"statusCode": 200, "body": json.dumps(response_data)}

        except ClientError as e:
            error_code = e.response["Error"].get("Code")

            # Handle various Cognito-specific exceptions
            if error_code == "NotAuthorizedException":
                signal.alarm(0)  # Cancel timeout
                return {
                    "statusCode": 401,
                    "body": json.dumps(
                        {"error": "Invalid code or authentication failed"}
                    ),
                }
            elif error_code == "CodeMismatchException":
                signal.alarm(0)  # Cancel timeout
                return {
                    "statusCode": 401,
                    "body": json.dumps({"error": "Invalid verification code"}),
                }
            elif error_code == "ExpiredCodeException":
                signal.alarm(0)  # Cancel timeout
                return {
                    "statusCode": 401,
                    "body": json.dumps({"error": "Verification code has expired"}),
                }
            elif error_code == "InvalidLambdaResponseException":
                signal.alarm(0)  # Cancel timeout
                return {
                    "statusCode": 500,
                    "body": json.dumps(
                        {"error": "Authentication service configuration error"}
                    ),
                }
            else:
                signal.alarm(0)  # Cancel timeout
                return {
                    "statusCode": 401,
                    "body": json.dumps({"error": f"Authentication failed: {str(e)}"}),
                }

    except TimeoutError as e:
        # Handle timeout specifically
        print(f"⏰ Lambda timeout error: {str(e)}")
        return {
            "statusCode": 504,
            "body": json.dumps({"error": "Request timeout - please try again"}),
        }
    except Exception as e:
        # Fallback for all other exceptions
        signal.alarm(0)  # Cancel timeout
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }
