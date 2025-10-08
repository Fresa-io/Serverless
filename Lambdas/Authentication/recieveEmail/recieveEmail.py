# Test comment for branch verification - fixed directory structure
import json
import boto3
import os
import random
import time
from datetime import datetime, timedelta, timezone

# Initialize AWS clients lazily to avoid issues during testing
_dynamodb_client = None
_ses_client = None


def get_dynamodb_client():
    """Get DynamoDB client with lazy initialization"""
    global _dynamodb_client
    if _dynamodb_client is None:
        aws_region = os.environ.get("AWS_REGION", "us-east-1")
        _dynamodb_client = boto3.client("dynamodb", region_name=aws_region)
    return _dynamodb_client


def get_ses_client():
    """Get SES client with lazy initialization"""
    global _ses_client
    if _ses_client is None:
        aws_region = os.environ.get("AWS_REGION", "us-east-1")
        _ses_client = boto3.client("ses", region_name=aws_region)
    return _ses_client


# Lazy loading of environment variables to avoid KeyError during testing
def get_dynamodb_table_name():
    return os.environ.get("DYNAMODB_TABLE_NAME")


def get_ses_from_email_address():
    return os.environ.get("SES_FROM_EMAIL_ADDRESS")


def get_ses_verification_template_name():
    return os.environ.get("SES_VERIFICATION_TEMPLATE_NAME")


CODE_EXPIRATION_MINUTES = 10

# Cooldown configurations
RATE_LIMIT_CONFIG = {
    "INITIAL_BURST_COUNT": 2,
    "INITIAL_BURST_WINDOW": 5 * 60,  # 5 minutes
    "SUBSEQUENT_COOLDOWN": 15 * 60,  # 15 minutes
    "RESET_THRESHOLD": 5 * 60 * 60,  # 5 hours
}


def generate_verification_code(length=6):
    """Generates a secure random numerical code using system randomness"""
    return "".join(str(random.SystemRandom().randint(0, 9)) for _ in range(length))


def validate_environment():
    """Validate all required environment variables are set"""
    required_vars = {
        "DYNAMODB_TABLE_NAME": get_dynamodb_table_name(),
        "SES_FROM_EMAIL_ADDRESS": get_ses_from_email_address(),
        "SES_VERIFICATION_TEMPLATE_NAME": get_ses_verification_template_name(),
    }
    missing = [var for var, val in required_vars.items() if not val]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )


def handle_rate_limiting(email):
    """Implement rate limiting logic with cooldown periods"""
    current_time = int(datetime.now(timezone.utc).timestamp())

    try:
        dynamodb_client = get_dynamodb_client()
        response = dynamodb_client.get_item(
            TableName=get_dynamodb_table_name(),
            Key={"email": {"S": email}},
            ProjectionExpression="requestHistory, lastRequestTime, postBurstCodeSent",
        )
    except dynamodb_client.exceptions.ClientError as e:
        print(f"DynamoDB Get Error: {str(e)}")
        raise

    request_history = []
    last_request_time = None
    post_burst_code_sent = False

    if "Item" in response:
        # Get all requests within the reset threshold
        request_history = [
            int(item["N"])
            for item in response["Item"].get("requestHistory", {}).get("L", [])
            if current_time - int(item["N"]) < RATE_LIMIT_CONFIG["RESET_THRESHOLD"]
        ]

        # Get the last request time
        if "lastRequestTime" in response["Item"]:
            last_request_time = int(response["Item"]["lastRequestTime"]["N"])

        # Check if we've already sent a code after the burst period
        if "postBurstCodeSent" in response["Item"]:
            post_burst_code_sent = response["Item"]["postBurstCodeSent"].get(
                "BOOL", False
            )

    # Sort request history to ensure chronological order
    request_history.sort()

    # Check if we have any requests
    if not request_history:
        return None  # No previous requests, allow this one

    # Step 1: Check if user is within their initial burst allowance
    if len(request_history) < RATE_LIMIT_CONFIG["INITIAL_BURST_COUNT"]:
        return None  # Still within burst allowance, allow the request

    # Step 2: User has reached burst limit, now check the burst window
    if len(request_history) >= RATE_LIMIT_CONFIG["INITIAL_BURST_COUNT"]:
        # Get the most recent burst count requests
        recent_requests = request_history[-RATE_LIMIT_CONFIG["INITIAL_BURST_COUNT"] :]
        time_since_first_in_burst = current_time - recent_requests[0]

        # If we're still within the burst window, block with shorter wait time
        if time_since_first_in_burst < RATE_LIMIT_CONFIG["INITIAL_BURST_WINDOW"]:
            remaining_burst_time = (
                RATE_LIMIT_CONFIG["INITIAL_BURST_WINDOW"] - time_since_first_in_burst
            )
            return {
                "statusCode": 429,
                "body": json.dumps(
                    {
                        "success": False,
                        "message": f"Rate limit exceeded. Please try again in {remaining_burst_time} seconds",
                    }
                ),
            }
        else:
            # Burst window has passed - now we need to check if we've already sent a post-burst code
            if not post_burst_code_sent:
                # This is the first request after burst window - allow it and mark post-burst code as sent
                return None
            else:
                # We've already sent the post-burst code, now enforce the longer cooldown
                time_since_last = current_time - request_history[-1]
                if time_since_last < RATE_LIMIT_CONFIG["SUBSEQUENT_COOLDOWN"]:
                    remaining_cooldown = (
                        RATE_LIMIT_CONFIG["SUBSEQUENT_COOLDOWN"] - time_since_last
                    )
                    return {
                        "statusCode": 429,
                        "body": json.dumps(
                            {
                                "success": False,
                                "message": f"Too many requests. Please try again in {remaining_cooldown} seconds",
                            }
                        ),
                    }

    return None


def update_dynamo_record(email, code, is_post_burst_code=False):
    """Update DynamoDB with new verification code and request history"""
    current_time = datetime.now(timezone.utc)
    expiration_time = current_time + timedelta(minutes=CODE_EXPIRATION_MINUTES)

    # Base update expression
    update_expression = """
        SET #code = :code,
            #ttl = :ttl,
            createdAt = :createdAt,
            lastRequestTime = :lastRequestTime,
            requestHistory = list_append(if_not_exists(requestHistory, :emptyList), :newRequest)
    """

    expression_attribute_names = {"#code": "code", "#ttl": "ttl"}

    expression_attribute_values = {
        ":code": {"S": code},
        ":ttl": {"N": str(int(expiration_time.timestamp()))},
        ":createdAt": {"S": current_time.isoformat()},
        ":lastRequestTime": {"N": str(int(current_time.timestamp()))},
        ":newRequest": {"L": [{"N": str(int(current_time.timestamp()))}]},
        ":emptyList": {"L": []},
    }

    # If this is a post-burst code, mark it as sent
    if is_post_burst_code:
        update_expression += ", postBurstCodeSent = :postBurstCodeSent"
        expression_attribute_values[":postBurstCodeSent"] = {"BOOL": True}

    try:
        dynamodb_client = get_dynamodb_client()
        dynamodb_client.update_item(
            TableName=get_dynamodb_table_name(),
            Key={"email": {"S": email}},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
        )
    except dynamodb_client.exceptions.ClientError as e:
        print(f"DynamoDB Update Error: {str(e)}")
        raise


def send_verification_email(email, code):
    """Send templated email using predefined SES template"""
    try:
        ses_client = get_ses_client()
        ses_client.send_templated_email(
            Source=get_ses_from_email_address(),
            Destination={"ToAddresses": [email]},
            Template=get_ses_verification_template_name(),
            TemplateData=json.dumps(
                {"verificationCode": code, "expirationMinutes": CODE_EXPIRATION_MINUTES}
            ),
        )
    except ses_client.exceptions.ClientError as e:
        print(f"SES Send Error: {str(e)}")
        raise


def check_user_exists_in_cognito(email):
    """Check if user exists in Cognito User Pool"""
    try:
        cognito = boto3.client("cognito-idp")
        user_pool_id = os.environ.get("COGNITO_USER_POOL_ID")
        
        if not user_pool_id:
            print("❌ COGNITO_USER_POOL_ID not set")
            return False
            
        cognito.admin_get_user(UserPoolId=user_pool_id, Username=email)
        return True
    except cognito.exceptions.UserNotFoundException:
        return False
    except Exception as e:
        print(f"❌ Error checking user existence: {str(e)}")
        return False


def determine_if_post_burst_code(email):
    """Determine if this code is being sent after the burst period"""
    current_time = int(datetime.now(timezone.utc).timestamp())

    try:
        dynamodb_client = get_dynamodb_client()
        response = dynamodb_client.get_item(
            TableName=get_dynamodb_table_name(),
            Key={"email": {"S": email}},
            ProjectionExpression="requestHistory, postBurstCodeSent",
        )
    except dynamodb_client.exceptions.ClientError as e:
        print(f"DynamoDB Get Error in determine_if_post_burst_code: {str(e)}")
        return False

    if "Item" not in response:
        return False

    # Get request history within reset threshold
    request_history = [
        int(item["N"])
        for item in response["Item"].get("requestHistory", {}).get("L", [])
        if current_time - int(item["N"]) < RATE_LIMIT_CONFIG["RESET_THRESHOLD"]
    ]

    # Check if we've already marked post-burst code as sent
    post_burst_code_sent = (
        response["Item"].get("postBurstCodeSent", {}).get("BOOL", False)
    )

    # If we have reached the burst count, burst window has passed, and we haven't sent post-burst code yet
    if (
        len(request_history) >= RATE_LIMIT_CONFIG["INITIAL_BURST_COUNT"]
        and not post_burst_code_sent
    ):
        request_history.sort()
        recent_requests = request_history[-RATE_LIMIT_CONFIG["INITIAL_BURST_COUNT"] :]
        time_since_first_in_burst = current_time - recent_requests[0]

        if time_since_first_in_burst >= RATE_LIMIT_CONFIG["INITIAL_BURST_WINDOW"]:
            return True

    return False


def lambda_handler(event, context):
    try:
        validate_environment()
        email = (event.get("queryStringParameters") or {}).get("email")

        if not email:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"success": False, "message": "Email parameter is required"}
                ),
            }

        # Convert email to lowercase for consistent processing
        email = email.lower().strip()

        # Check if user exists in Cognito
        if not check_user_exists_in_cognito(email):
            return {
                "statusCode": 404,
                "body": json.dumps(
                    {
                        "success": False, 
                        "message": "Email address not found. Please check your email address or sign up first."
                    }
                ),
            }

        rate_limit_response = handle_rate_limiting(email)
        if rate_limit_response:
            return rate_limit_response

        # Determine if this is a post-burst code
        is_post_burst_code = determine_if_post_burst_code(email)

        verification_code = generate_verification_code()
        update_dynamo_record(email, verification_code, is_post_burst_code)
        send_verification_email(email, verification_code)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"success": True, "message": f"Verification code sent to {email}"}
            ),
        }
    except Exception as e:
        print(f"Critical Error: {str(e)}")
        
        # Check if it's a specific error we can handle
        error_message = str(e).lower()
        if "user not found" in error_message or "does not exist" in error_message:
            return {
                "statusCode": 404,
                "body": json.dumps(
                    {
                        "success": False,
                        "message": "Email address not found. Please check your email address or sign up first."
                    }
                ),
            }
        elif "rate limit" in error_message or "throttl" in error_message:
            return {
                "statusCode": 429,
                "body": json.dumps(
                    {
                        "success": False,
                        "message": "Too many requests. Please wait before requesting another code."
                    }
                ),
            }
        elif "ses" in error_message or "email" in error_message:
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {
                        "success": False,
                        "message": "Unable to send email. Please try again later."
                    }
                ),
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {
                        "success": False,
                        "message": "Internal server error. Please try again later.",
                    }
                ),
            }
