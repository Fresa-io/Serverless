#!/usr/bin/env python3
"""
Unit tests for verifyAuthChallenge Lambda function
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
import verifyAuthChallenge


class TestVerifyauthchallenge(unittest.TestCase):
    """Test cases for verifyAuthChallenge function"""

    def setUp(self):
        """Set up test fixtures"""
        # Set required environment variables for testing
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_test123"
        os.environ["COGNITO_CLIENT_ID"] = "test_client_id"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["DYNAMODB_TABLE_NAME"] = "test-verification-codes"
        os.environ["CODE_EXPIRATION_MINUTES"] = "10"

        self.test_event = {
            "httpMethod": "POST",
            "body": json.dumps({"email": "test@example.com", "code": "123456"}),
        }

        self.test_context = {
            "function_name": "verifyAuthChallenge",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:verifyAuthChallenge:$LATEST",
            "memory_limit_in_mb": "128",
            "aws_request_id": "test-request-id",
            "log_group_name": "/aws/lambda/verifyAuthChallenge",
            "log_stream_name": "test-log-stream",
        }

    @patch("verifyAuthChallenge.get_cognito_client")
    @patch("verifyAuthChallenge.get_dynamodb_resource")
    def test_verifyAuthChallenge_success(
        self, mock_dynamodb_resource, mock_cognito_client
    ):
        """Test successful verifyAuthChallenge execution"""
        # Mock Cognito client
        mock_cognito = MagicMock()
        mock_cognito_client.return_value = mock_cognito
        mock_cognito.admin_get_user.return_value = {}
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

        # Mock DynamoDB
        mock_dynamodb = MagicMock()
        mock_dynamodb_resource.return_value = mock_dynamodb
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        current_time = int(time.time())
        mock_table.get_item.return_value = {
            "Item": {"code": "123456", "lastRequestTime": current_time}
        }

        result = verifyAuthChallenge.lambda_handler(self.test_event, self.test_context)

        self.assertEqual(result["statusCode"], 200)
        self.assertIn("access_token", json.loads(result["body"]))

    def test_verifyAuthChallenge_invalid_event(self):
        """Test verifyAuthChallenge with invalid event"""
        invalid_event = {}
        result = verifyAuthChallenge.lambda_handler(invalid_event, self.test_context)

        self.assertEqual(
            result["statusCode"], 500
        )  # Should return 500 for invalid event


if __name__ == "__main__":
    unittest.main()
