#!/usr/bin/env python3
"""
Unit tests for identity_provider_auth Lambda function
"""

import unittest
import json
import sys
import os

# Add the function directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function module
import identity_provider_auth


class TestIdentityproviderauth(unittest.TestCase):
    """Test cases for identity_provider_auth function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_event = {"httpMethod": "POST", "body": json.dumps({"test": "data"})}

        self.test_context = {
            "function_name": "identity_provider_auth",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:identity_provider_auth:$LATEST",
            "memory_limit_in_mb": "128",
            "aws_request_id": "test-request-id",
            "log_group_name": "/aws/lambda/identity_provider_auth",
            "log_stream_name": "test-log-stream",
        }

    def test_identity_provider_auth_success(self):
        """Test successful identity_provider_auth execution"""
        result = identity_provider_auth.lambda_handler(
            self.test_event, self.test_context
        )

        self.assertEqual(result["statusCode"], 200)
        self.assertIn("message", json.loads(result["body"]))

    def test_identity_provider_auth_invalid_event(self):
        """Test identity_provider_auth with invalid event"""
        invalid_event = {}
        result = identity_provider_auth.lambda_handler(invalid_event, self.test_context)

        self.assertEqual(
            result["statusCode"], 200
        )  # Should still work with empty event


if __name__ == "__main__":
    unittest.main()
