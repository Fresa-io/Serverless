#!/usr/bin/env python3
"""
Unit tests for social_auth_user Lambda function
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add the function directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function module
import social_auth_user


class TestSocialauthuser(unittest.TestCase):
    """Test cases for social_auth_user function"""

    def setUp(self):
        """Set up test fixtures"""
        # Set required environment variables for testing
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_test123"
        os.environ["COGNITO_CLIENT_ID"] = "test_client_id"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["SENDER_EMAIL"] = "test@example.com"

        self.test_event = {
            "httpMethod": "POST",
            "pathParameters": {"provider": "google"},
            "body": json.dumps(
                {
                    "idToken": "test-google-id-token",
                    "gender": "Male",
                    "dateOfBirth": "1990-01-01",
                }
            ),
        }

        self.test_context = {
            "function_name": "social_auth_user",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:social_auth_user:$LATEST",
            "memory_limit_in_mb": "128",
            "aws_request_id": "test-request-id",
            "log_group_name": "/aws/lambda/social_auth_user",
            "log_stream_name": "test-log-stream",
        }

    @patch("social_auth_user.get_cognito_client")
    @patch("social_auth_user.get_ses_client")
    @patch("social_auth_user.verify_google_token")
    def test_social_auth_user_success(
        self, mock_verify_token, mock_ses_client, mock_cognito_client
    ):
        """Test successful social_auth_user execution"""
        # Mock Google token verification
        mock_verify_token.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
        }

        # Mock Cognito client
        mock_cognito = MagicMock()
        mock_cognito_client.return_value = mock_cognito
        mock_cognito.admin_get_user.side_effect = Exception(
            "User not found"
        )  # User doesn't exist
        mock_cognito.admin_create_user.return_value = {}
        mock_cognito.admin_set_user_password.return_value = {}
        mock_cognito.admin_initiate_auth.return_value = {
            "AuthenticationResult": {
                "AccessToken": "test-access-token",
                "IdToken": "test-id-token",
                "RefreshToken": "test-refresh-token",
            }
        }

        # Mock SES client
        mock_ses = MagicMock()
        mock_ses_client.return_value = mock_ses

        result = social_auth_user.lambda_handler(self.test_event, self.test_context)

        self.assertEqual(result["statusCode"], 200)
        self.assertIn("message", json.loads(result["body"]))

    def test_social_auth_user_invalid_event(self):
        """Test social_auth_user with invalid event"""
        invalid_event = {}
        result = social_auth_user.lambda_handler(invalid_event, self.test_context)

        self.assertEqual(
            result["statusCode"], 400
        )  # Should return 400 for invalid event


if __name__ == "__main__":
    unittest.main()
