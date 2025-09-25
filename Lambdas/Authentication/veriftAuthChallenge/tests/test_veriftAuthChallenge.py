#!/usr/bin/env python3
"""
Unit tests for veriftAuthChallenge Lambda function
"""

import unittest
import json
import sys
import os

# Add the function directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function module
import veriftAuthChallenge


class TestVeriftauthchallenge(unittest.TestCase):
    """Test cases for veriftAuthChallenge function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_event = {"httpMethod": "POST", "body": json.dumps({"test": "data"})}

        self.test_context = {
            "function_name": "veriftAuthChallenge",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:veriftAuthChallenge:$LATEST",
            "memory_limit_in_mb": "128",
            "aws_request_id": "test-request-id",
            "log_group_name": "/aws/lambda/veriftAuthChallenge",
            "log_stream_name": "test-log-stream",
        }

    def test_veriftAuthChallenge_success(self):
        """Test successful veriftAuthChallenge execution"""
        result = veriftAuthChallenge.veriftAuthChallenge(
            self.test_event, self.test_context
        )

        self.assertEqual(result["statusCode"], 200)
        self.assertIn("message", json.loads(result["body"]))

    def test_veriftAuthChallenge_invalid_event(self):
        """Test veriftAuthChallenge with invalid event"""
        invalid_event = {}
        result = veriftAuthChallenge.veriftAuthChallenge(
            invalid_event, self.test_context
        )

        self.assertEqual(
            result["statusCode"], 200
        )  # Should still work with empty event


if __name__ == "__main__":
    unittest.main()
