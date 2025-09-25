import json
import boto3
import secrets
import string
import os
import time
from botocore.exceptions import ClientError

# Initialize DynamoDB resource lazily to avoid issues during testing
_dynamodb = None


def get_dynamodb_resource():
    """Get DynamoDB resource with lazy initialization"""
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb")
    return _dynamodb


# Generate a secure random password
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


def validate_verification_code(email, user_code):
    """Validate verification code against DynamoDB with enhanced checks"""
    try:
        table_name = os.environ.get("DYNAMODB_TABLE_NAME")
        if not table_name:
            print("DYNAMODB_TABLE_NAME environment variable not set")
            return False, "Configuration error"

        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(table_name)
        code_expiration_minutes = int(os.environ.get("CODE_EXPIRATION_MINUTES", "10"))

        # Get stored code and lastRequestTime from DynamoDB
        response = table.get_item(Key={"email": email.lower()})

        if "Item" not in response:
            print(f"No DynamoDB record found for email: {email}")
            return False, "Code not found or expired"

        item = response["Item"]

        # Validate required fields exist
        if "code" not in item or "lastRequestTime" not in item:
            print(f"Missing fields in DynamoDB record for {email}")
            return False, "Code not found or expired"

        stored_code = item["code"]
        last_request_time = item["lastRequestTime"]

        # Handle different number types (int/float/string)
        try:
            last_request_time = int(float(last_request_time))
        except (TypeError, ValueError):
            print(f"Invalid timestamp format for {email}: {last_request_time}")
            return False, "Invalid timestamp format"

        # Check expiration FIRST (security best practice)
        current_time = int(time.time())
        expiration_time = last_request_time + (code_expiration_minutes * 60)

        if current_time > expiration_time:
            print(
                f"Code expired for {email}. Current: {current_time}, Expiration: {expiration_time}"
            )
            return False, "Code has expired"

        # Validate code after passing expiration check
        if user_code != stored_code:
            print(f"Invalid code provided for {email}")
            return False, "Invalid verification code"

        print(f"Code validation successful for {email}")
        return True, "Code is valid"

    except ClientError as e:
        print(f"DynamoDB error for {email}: {str(e)}")
        return False, "Database error occurred"
    except Exception as e:
        print(f"Unexpected error validating code for {email}: {str(e)}")
        return False, "Validation error occurred"


def get_gendered_template_data(name, gender):
    """
    Helper function to generate gender-appropriate template data
    """
    if gender.lower() == "female":
        return {
            "name": name,
            "greeting": "Bienvenida",
            "excitement_message": "Estamos emocionados de tenerte con nosotros",
            "design_description": "diseñado",
        }
    else:  # default to male
        return {
            "name": name,
            "greeting": "Bienvenido",
            "excitement_message": "Estamos emocionados de tenerte con nosotros",
            "design_description": "diseñado",
        }


def send_welcome_email(email, first_name, gender):
    """Send welcome email using SES template"""
    try:
        # Initialize SES client
        ses_client = boto3.client(
            "ses", region_name=os.environ.get("AWS_REGION", "us-east-1")
        )

        # Get sender email from environment variable
        sender_email = os.environ.get("SENDER_EMAIL", "admin@fresa.live")

        # Get gendered template data
        template_data = get_gendered_template_data(first_name, gender)

        print(f"Sending welcome email to {email} with template data: {template_data}")

        # Send templated email
        response = ses_client.send_templated_email(
            Source=sender_email,
            Destination={"ToAddresses": [email]},
            Template="fresa-welcome-template",
            TemplateData=json.dumps(template_data),
        )

        print(
            f"Welcome email sent successfully to {email}. MessageId: {response['MessageId']}"
        )
        return True

    except ClientError as e:
        print(f"Failed to send welcome email to {email}: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error sending welcome email to {email}: {str(e)}")
        return False


def lambda_handler(event, context):
    # Get configuration from environment variables
    USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
    CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")

    if not USER_POOL_ID or not CLIENT_ID:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps(
                {
                    "error": "Missing required environment variables: COGNITO_USER_POOL_ID and/or COGNITO_CLIENT_ID"
                }
            ),
        }

    try:
        # Parse the request body
        body = json.loads(event["body"])
        email = body["email"].lower()
        code = body["code"]

        # FIRST: Validate verification code against DynamoDB
        code_valid, validation_message = validate_verification_code(email, code)

        if not code_valid:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": json.dumps(
                    {
                        "error": validation_message,
                        "message": "Please check your verification code or request a new one.",
                    }
                ),
            }

        # Only proceed with user creation if code is valid
        first_name = body["firstName"]
        last_name = body["lastName"]
        date_of_birth = body["dateOfBirth"]
        gender = body["gender"]
        user_newly_created = False
        cognito = boto3.client("cognito-idp")

        # Create user in Cognito User Pool
        try:
            create_response = cognito.admin_create_user(
                UserPoolId=USER_POOL_ID,
                Username=email,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "given_name", "Value": first_name},
                    {"Name": "family_name", "Value": last_name},
                    {"Name": "birthdate", "Value": date_of_birth},
                    {"Name": "gender", "Value": gender},
                    {"Name": "email_verified", "Value": "true"},
                ],
                MessageAction="SUPPRESS",  # Don't send welcome email
                TemporaryPassword=generate_random_password(12),
            )

            # Set permanent password with generated random password
            cognito.admin_set_user_password(
                UserPoolId=USER_POOL_ID,
                Username=email,
                Password=generate_random_password(),
                Permanent=True,
            )

            print(f"User {email} created successfully")
            user_newly_created = True

        except ClientError as e:
            if e.response["Error"]["Code"] == "UsernameExistsException":
                print(f"User {email} already exists, proceeding with authentication")
            else:
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    },
                    "body": json.dumps({"error": f"Failed to create user: {str(e)}"}),
                }

        # Now proceed with custom auth flow
        try:
            # Initiate custom auth flow
            auth_response = cognito.initiate_auth(
                ClientId=CLIENT_ID,
                AuthFlow="CUSTOM_AUTH",
                AuthParameters={"USERNAME": email},
            )

            # Respond to custom challenge with the provided code
            challenge_response = cognito.respond_to_auth_challenge(
                ClientId=CLIENT_ID,
                ChallengeName="CUSTOM_CHALLENGE",
                Session=auth_response["Session"],
                ChallengeResponses={"USERNAME": email, "ANSWER": code},
            )

            # Extract tokens from successful authentication
            auth_result = challenge_response["AuthenticationResult"]

            # Send welcome email only if user was newly created
            email_sent = False
            if user_newly_created:
                email_sent = send_welcome_email(email, first_name, gender)

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": json.dumps(
                    {
                        "message": "Authentication successful",
                        "tokens": {
                            "AccessToken": auth_result["AccessToken"],
                            "IdToken": auth_result["IdToken"],
                            "RefreshToken": auth_result["RefreshToken"],
                            "TokenType": auth_result["TokenType"],
                            "ExpiresIn": auth_result["ExpiresIn"],
                        },
                        "userInfo": {
                            "email": email,
                            "firstName": first_name,
                            "lastName": last_name,
                            "dateOfBirth": date_of_birth,
                            "gender": gender,
                        },
                        "welcomeEmailSent": email_sent,
                    }
                ),
            }

        except ClientError as auth_error:
            error_code = auth_error.response["Error"]["Code"]
            error_msg = str(auth_error)

            if error_code == "NotAuthorizedException":
                return {
                    "statusCode": 401,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    },
                    "body": json.dumps(
                        {
                            "error": "Authentication failed: Invalid credentials",
                            "code": error_code,
                        }
                    ),
                }
            else:
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    },
                    "body": json.dumps(
                        {
                            "error": f"Authentication failed: {error_msg}",
                            "code": error_code,
                        }
                    ),
                }

    except KeyError as e:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps({"error": f"Missing required field: {str(e)}"}),
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps({"error": "Invalid JSON in request body"}),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }
