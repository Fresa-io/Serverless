import json
import boto3
import os
import urllib3
import logging
import secrets
import string
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services lazily to avoid issues during testing
_cognito = None
_http = None


def get_cognito_client():
    """Get Cognito client with lazy initialization"""
    global _cognito
    if _cognito is None:
        _cognito = boto3.client("cognito-idp")
    return _cognito


def get_http_pool():
    """Get HTTP pool with lazy initialization"""
    global _http
    if _http is None:
        _http = urllib3.PoolManager()
    return _http


# Lazy loading of environment variables to avoid KeyError during testing
def get_client_id():
    return os.environ["COGNITO_CLIENT_ID"]


def get_user_pool_id():
    return os.environ["COGNITO_USER_POOL_ID"]


def verify_google_token(id_token_string):
    """Verify Google ID token and extract user information"""
    logger.info("Starting Google token verification")
    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token_string}"
        http = get_http_pool()
        response = http.request("GET", url)
        if response.status != 200:
            return {"success": False, "error": "Invalid Google token"}
        token_info = json.loads(response.data.decode("utf-8"))
        if "error" in token_info:
            return {
                "success": False,
                "error": token_info.get("error_description", "Invalid token"),
            }

        email = token_info.get("email", "").lower()
        return {
            "success": True,
            "email": email,
            "first_name": token_info.get("given_name", ""),
            "last_name": token_info.get("family_name", ""),
            "picture": token_info.get("picture", ""),
        }
    except Exception as e:
        logger.error(f"Google verification failed: {str(e)}")
        return {"success": False, "error": f"Google verification failed: {str(e)}"}


def verify_facebook_token(access_token):
    """Verify Facebook access token and extract user information"""
    logger.info("Starting Facebook token verification")
    try:
        url = f"https://graph.facebook.com/me?fields=id,email,first_name,last_name,picture&access_token={access_token}"
        http = get_http_pool()
        response = http.request("GET", url)
        if response.status != 200:
            return {"success": False, "error": "Invalid Facebook token"}
        user_data = json.loads(response.data.decode("utf-8"))
        if "error" in user_data:
            return {"success": False, "error": user_data["error"]["message"]}

        email = user_data.get("email", "").lower()
        return {
            "success": True,
            "email": email,
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name", ""),
            "picture": user_data.get("picture", {}).get("data", {}).get("url", ""),
        }
    except Exception as e:
        logger.error(f"Facebook verification failed: {str(e)}")
        return {"success": False, "error": f"Facebook verification failed: {str(e)}"}


def generate_random_password(length=16):
    """Generate a secure random password using cryptographically secure methods"""
    # Use environment variable for password complexity if available
    min_length = int(os.environ.get("MIN_PASSWORD_LENGTH", "16"))
    length = max(length, min_length)

    # Define character sets for password complexity
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special_chars = "!@#$%^&*"
    all_chars = uppercase + lowercase + digits + special_chars

    # Ensure at least one character from each set
    password_chars = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special_chars),
    ]

    # Fill the rest with random characters
    for _ in range(length - 4):
        password_chars.append(secrets.choice(all_chars))

    # Shuffle the password characters
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


def authenticate_social_user_with_cognito(email):
    """Authenticate social user by setting a temporary password and authenticating"""
    logger.info(f"Authenticating existing social user: {email}")
    try:
        # Generate a temporary password for authentication
        temp_password = generate_random_password()

        # Set the temporary password
        cognito = get_cognito_client()
        cognito.admin_set_user_password(
            UserPoolId=get_user_pool_id(),
            Username=email,
            Password=temp_password,
            Permanent=True,
        )

        # Now authenticate with the temporary password
        auth_response = cognito.admin_initiate_auth(
            UserPoolId=get_user_pool_id(),
            ClientId=get_client_id(),
            AuthFlow="ADMIN_NO_SRP_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": temp_password},
        )

        logger.info(f"Successfully authenticated social user: {email}")
        return {"success": True, "tokens": auth_response["AuthenticationResult"]}

    except ClientError as e:
        logger.error(f"Authentication failed for {email}: {str(e)}")
        return {"success": False, "error": f"Authentication failed: {str(e)}"}


def lambda_handler(event, context):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST",
    }

    try:
        provider = event.get("pathParameters", {}).get("provider", "").lower()
        if provider not in ["google", "facebook"]:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Invalid provider."}),
            }

        body = json.loads(event["body"])
        token = body.get("accessToken") or body.get("idToken")
        if not token:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Missing access/id token."}),
            }

        user_info = {}
        if provider == "google":
            user_info = verify_google_token(token)
        elif provider == "facebook":
            user_info = verify_facebook_token(token)

        if not user_info.get("success"):
            return {
                "statusCode": 401,
                "headers": headers,
                "body": json.dumps(
                    {"error": user_info.get("error", "Token verification failed.")}
                ),
            }

        email = user_info["email"]
        if not email:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Email not provided by social provider."}),
            }

        # Check if the user exists in Cognito
        try:
            cognito = get_cognito_client()
            user_details = cognito.admin_get_user(
                UserPoolId=get_user_pool_id(), Username=email
            )
            logger.info(f"User {email} found in Cognito. Authenticating...")

            # User exists, so authenticate and return tokens
            auth_result = authenticate_social_user_with_cognito(email)
            if not auth_result.get("success"):
                return {
                    "statusCode": 500,
                    "headers": headers,
                    "body": json.dumps({"error": auth_result.get("error")}),
                }

            # Build user info from Cognito attributes
            user_attributes = {
                attr["Name"]: attr["Value"] for attr in user_details["UserAttributes"]
            }

            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(
                    {
                        "success": True,
                        "isNewUser": False,
                        "tokens": auth_result["tokens"],
                        "userInfo": {
                            "email": email,
                            "firstName": user_attributes.get("given_name", ""),
                            "lastName": user_attributes.get("family_name", ""),
                            "name": f"{user_attributes.get('given_name', '')} {user_attributes.get('family_name', '')}".strip(),
                            "picture": user_attributes.get("picture", ""),
                            "provider": provider,
                        },
                    }
                ),
            }

        except ClientError as e:
            if e.response["Error"]["Code"] == "UserNotFoundException":
                logger.info(
                    f"User {email} not found. Signaling client to proceed with creation."
                )
                # User does not exist, return a 404 with user details for the next step
                return {
                    "statusCode": 404,
                    "headers": headers,
                    "body": json.dumps(
                        {
                            "success": False,
                            "message": "User not found. Proceed to create user.",
                            "userInfo": {
                                "email": email,
                                "firstName": user_info.get("first_name"),
                                "lastName": user_info.get("last_name"),
                                "picture": user_info.get("picture"),
                                "provider": provider,
                            },
                        }
                    ),
                }
            else:
                raise e  # Re-raise other Cognito errors

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }
