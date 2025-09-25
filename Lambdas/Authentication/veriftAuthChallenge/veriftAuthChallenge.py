import os
import json
import boto3
import time
from datetime import datetime, timezone
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMODB_TABLE_NAME"])
CODE_EXPIRATION_MINUTES = int(os.environ.get("CODE_EXPIRATION_MINUTES", "10"))


def lambda_handler(event, context):
    try:
        # Get user input and email
        user_code = event["request"]["challengeAnswer"]
        username = event["request"]["userAttributes"].get("email", "")

        if not username:
            print("No email found in user attributes")
            event["response"] = {"answerCorrect": False}
            event["version"] = 1
            return event

        # Get stored code and lastRequestTime from DynamoDB
        try:
            response = table.get_item(Key={"email": username.lower()})

            if "Item" not in response:
                print(f"No DynamoDB record found for email: {username}")
                event["response"] = {"answerCorrect": False}
                event["version"] = 1
                return event

            item = response["Item"]
            stored_code = item.get("code", "")
            last_request_time = item.get("lastRequestTime")

            # Check if code has expired
            if last_request_time:
                current_time = int(time.time())
                expiration_time = last_request_time + (CODE_EXPIRATION_MINUTES * 60)

                if current_time > expiration_time:
                    print(
                        f"Code expired for {username}. Current: {current_time}, Expiration: {expiration_time}"
                    )
                    event["response"] = {"answerCorrect": False}
                    event["version"] = 1
                    return event

            # Validate code
            is_valid = user_code == stored_code

            print(f"Code validation for {username}: {is_valid}")

        except ClientError as e:
            print(f"DynamoDB error: {str(e)}")
            event["response"] = {"answerCorrect": False}
            event["version"] = 1
            return event

        event["response"] = {"answerCorrect": is_valid}
        event["version"] = 1

        return event

    except Exception as e:
        print(f"VerifyAuthChallenge Error: {str(e)}")
        # Return valid structure even on failure
        event["response"] = {"answerCorrect": False}
        event["version"] = 1
        return event
