#!/usr/bin/env python3
"""
Unit tests for veriftAuthChallenge Lambda function
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
import veriftAuthChallenge


class TestVeriftauthchallenge(unittest.TestCase):
    """Test cases for veriftAuthChallenge function"""

    def setUp(self):
        """Set up test fixtures"""
        # Set required environment variables for testing
        os.environ["DYNAMODB_TABLE_NAME"] = "test-verification-codes"
        os.environ["AWS_REGION"] = "us-east-1"
        
        self.test_event = {
            "request": {
                "challengeAnswer": "123456",
                "userAttributes": {
                    "email": "test@example.com"
                }
            }
        }

        self.test_context = {
            "function_name": "veriftAuthChallenge",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:veriftAuthChallenge:$LATEST",
            "memory_limit_in_mb": "128",
            "aws_request_id": "test-request-id",
            "log_group_name": "/aws/lambda/veriftAuthChallenge",
            "log_stream_name": "test-log-stream",
        }

    @patch("veriftAuthChallenge.get_table")
    def test_veriftAuthChallenge_success(self, mock_get_table):
        """Test successful veriftAuthChallenge execution"""
        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        current_time = int(time.time())
        mock_table.get_item.return_value = {
            "Item": {
                "code": "123456",
                "lastRequestTime": current_time
            }
        }
        
        result = veriftAuthChallenge.lambda_handler(
            self.test_event, self.test_context
        )

        self.assertIn("response", result)
        self.assertIn("answerCorrect", result["response"])

    def test_veriftAuthChallenge_invalid_event(self):
        """Test veriftAuthChallenge with invalid event"""
        invalid_event = {}
        result = veriftAuthChallenge.lambda_handler(
            invalid_event, self.test_context
        )

        self.assertIn("response", result)
        self.assertIn("answerCorrect", result["response"])


if __name__ == "__main__":
    unittest.main()
