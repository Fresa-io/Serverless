import json
import boto3
import os
import secrets
import string
import logging
import urllib3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services
cognito = boto3.client("cognito-idp")
ses_client = boto3.client("ses", region_name=os.environ.get("AWS_REGION", "us-east-1"))

# Initialize urllib3
http = urllib3.PoolManager()

# Environment variables
CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]
USER_POOL_ID = os.environ["COGNITO_USER_POOL_ID"]
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "admin@fresa.live")


def verify_google_token(id_token_string):
    """Verify Google ID token and extract user information"""
    logger.info("Starting Google token verification")
    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token_string}"
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


def send_welcome_email(email, first_name, gender=None):
    """Send welcome email using SES template"""
    logger.info(f"Sending welcome email to: {email}")
    try:
        template_data = {"name": first_name or "Usuario"}
        # Optional: Customize email based on gender
        if gender and gender.lower() == "female":
            template_data["greeting"] = "Bienvenida"
        else:
            template_data["greeting"] = "Bienvenido"

        ses_client.send_templated_email(
            Source=SENDER_EMAIL,
            Destination={"ToAddresses": [email]},
            Template="fresa-welcome-template",  # Make sure this template exists in SES
            TemplateData=json.dumps(template_data),
        )
        logger.info(f"Successfully sent welcome email to: {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        return False


def lambda_handler(event, context):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST",
    }

    try:
        # Get provider from path parameters
        provider = event.get("pathParameters", {}).get("provider", "").lower()
        if provider not in ["google", "facebook"]:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Invalid provider."}),
            }

        body = json.loads(event["body"])

        # Get token from request
        token = body.get("accessToken") or body.get("idToken")
        if not token:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Missing access/id token."}),
            }

        # Get additional profile data from request
        gender = body.get("gender")
        birthdate = body.get("birthdate") or body.get(
            "dateOfBirth"
        )  # Support both field names

        # Optional override names (if provided, use these instead of token data)
        override_first_name = body.get("firstName")
        override_last_name = body.get("lastName")

        if not all([gender, birthdate]):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps(
                    {"error": "Missing required fields: gender, birthdate/dateOfBirth."}
                ),
            }

        # 1. Verify the social provider token and extract user info
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

        # Extract user data from token
        email = user_info["email"]
        first_name = override_first_name or user_info.get("first_name", "")
        last_name = override_last_name or user_info.get("last_name", "")
        picture_url = user_info.get("picture", "")

        if not email:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Email not provided by social provider."}),
            }

        # 2. Double-check that user doesn't exist (safety check)
        try:
            cognito.admin_get_user(UserPoolId=USER_POOL_ID, Username=email)
            # If we get here, user exists - this shouldn't happen in normal flow
            logger.warning(
                f"User {email} already exists but Lambda 2 was called. This indicates a race condition."
            )
            return {
                "statusCode": 409,
                "headers": headers,
                "body": json.dumps({"error": "User already exists."}),
            }
        except ClientError as e:
            if e.response["Error"]["Code"] != "UserNotFoundException":
                # Some other error occurred
                logger.error(f"Error checking user existence: {str(e)}")
                return {
                    "statusCode": 500,
                    "headers": headers,
                    "body": json.dumps({"error": f"Error checking user: {str(e)}"}),
                }
            # User doesn't exist - proceed with creation

        # 3. Create the user in Cognito
        logger.info(f"Creating new Cognito user: {email}")
        temp_password = generate_random_password()

        user_attributes = [
            {"Name": "email", "Value": email},
            {"Name": "email_verified", "Value": "true"},
            {"Name": "given_name", "Value": first_name},
            {"Name": "family_name", "Value": last_name},
            {"Name": "birthdate", "Value": birthdate},
            {"Name": "gender", "Value": gender},
        ]
        if picture_url:
            user_attributes.append({"Name": "picture", "Value": picture_url})

        try:
            cognito.admin_create_user(
                UserPoolId=USER_POOL_ID,
                Username=email,
                UserAttributes=user_attributes,
                TemporaryPassword=temp_password,
                MessageAction="SUPPRESS",  # Suppress the default welcome email
            )

            # Set the password to permanent
            cognito.admin_set_user_password(
                UserPoolId=USER_POOL_ID,
                Username=email,
                Password=temp_password,
                Permanent=True,
            )
            logger.info(f"Successfully created Cognito user: {email}")

        except ClientError as e:
            if e.response["Error"]["Code"] == "UsernameExistsException":
                # Race condition - user was created between our check and creation
                logger.warning(
                    f"User {email} was created by another process. Attempting to authenticate instead."
                )
            else:
                logger.error(f"Error creating Cognito user: {str(e)}")
                return {
                    "statusCode": 500,
                    "headers": headers,
                    "body": json.dumps({"error": f"Could not create user: {str(e)}"}),
                }

        # 4. Authenticate the newly created user
        logger.info(f"Authenticating new user: {email}")
        try:
            auth_response = cognito.admin_initiate_auth(
                UserPoolId=USER_POOL_ID,
                ClientId=CLIENT_ID,
                AuthFlow="ADMIN_NO_SRP_AUTH",
                AuthParameters={"USERNAME": email, "PASSWORD": temp_password},
            )
        except ClientError as e:
            logger.error(f"Authentication failed for new user {email}: {str(e)}")
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps(
                    {"error": f"User created but authentication failed: {str(e)}"}
                ),
            }

        # 5. Send the custom welcome email (asynchronously)
        send_welcome_email(email, first_name, gender)

        # 6. Return the tokens and user info
        return {
            "statusCode": 201,  # 201 Created
            "headers": headers,
            "body": json.dumps(
                {
                    "success": True,
                    "isNewUser": True,
                    "tokens": auth_response["AuthenticationResult"],
                    "userInfo": {
                        "email": email,
                        "firstName": first_name,
                        "lastName": last_name,
                        "name": f"{first_name} {last_name}",
                        "picture": picture_url,
                        "provider": provider,
                    },
                    "welcomeEmailSent": True,
                }
            ),
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Invalid JSON in request body."}),
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }
