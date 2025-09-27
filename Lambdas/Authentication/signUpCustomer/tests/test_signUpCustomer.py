#!/usr/bin/env python3
"""
Unit tests for signUpCustomer Lambda function
"""

import unittest
import json
import sys
import os
import time
from unittest.mock import patch, MagicMock

# Add the function directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function module
import signUpCustomer


class TestSignupcustomer(unittest.TestCase):
    """Test cases for signUpCustomer function"""

    def setUp(self):
        """Set up test fixtures"""
        # Set required environment variables for testing
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_test123"
        os.environ["COGNITO_CLIENT_ID"] = "test_client_id"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["DYNAMODB_TABLE_NAME"] = "test-verification-codes"

        self.test_event = {
            "httpMethod": "POST",
            "body": json.dumps(
                {
                    "email": "test@example.com",
                    "code": "123456",
                    "firstName": "John",
                    "lastName": "Doe",
                    "dateOfBirth": "1990-01-01",
                    "gender": "Male",
                }
            ),
        }

        self.test_context = {
            "function_name": "signUpCustomer",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:signUpCustomer:$LATEST",
            "memory_limit_in_mb": "128",
            "aws_request_id": "test-request-id",
            "log_group_name": "/aws/lambda/signUpCustomer",
            "log_stream_name": "test-log-stream",
        }

    @patch("signUpCustomer.get_dynamodb_resource")
    @patch("boto3.client")
    def test_signUpCustomer_success(self, mock_boto3_client, mock_dynamodb_resource):
        """Test successful signUpCustomer execution"""
        # Mock DynamoDB
        mock_dynamodb = MagicMock()
        mock_dynamodb_resource.return_value = mock_dynamodb
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        current_time = int(time.time())
        mock_table.get_item.return_value = {
            "Item": {"code": "123456", "lastRequestTime": current_time}
        }

        # Mock SES client
        mock_ses = MagicMock()
        mock_cognito = MagicMock()
        mock_boto3_client.side_effect = lambda service, **kwargs: (
            mock_ses if service == "ses" else mock_cognito
        )

        # Mock Cognito authentication responses
        mock_cognito.initiate_auth.return_value = {"Session": "test-session-id"}
        mock_cognito.respond_to_auth_challenge.return_value = {
            "AuthenticationResult": {
                "AccessToken": "test-access-token",
                "IdToken": "test-id-token",
                "RefreshToken": "test-refresh-token",
                "TokenType": "Bearer",
                "ExpiresIn": 3600,
            }
        }

        result = signUpCustomer.lambda_handler(self.test_event, self.test_context)

        self.assertEqual(result["statusCode"], 200)
        self.assertIn("message", json.loads(result["body"]))

    def test_signUpCustomer_invalid_event(self):
        """Test signUpCustomer with invalid event"""
        invalid_event = {}
        result = signUpCustomer.lambda_handler(invalid_event, self.test_context)

        self.assertEqual(
            result["statusCode"], 400
        )  # Should return 400 for invalid event


if __name__ == "__main__":
    unittest.main()
