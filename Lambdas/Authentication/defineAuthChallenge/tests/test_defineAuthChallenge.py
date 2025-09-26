#!/usr/bin/env python3
"""
Unit tests for defineAuthChallenge Lambda function
"""

import unittest
import json
import sys
import os

# Add the function directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function module
import defineAuthChallenge


class TestDefineauthchallenge(unittest.TestCase):
    """Test cases for defineAuthChallenge function"""

    def setUp(self):
        """Set up test fixtures"""
        # Cognito trigger event structure
        self.test_event = {
            "request": {
                "session": [
                    {
                        "challengeName": "CUSTOM_CHALLENGE",
                        "challengeResult": True,
                        "challengeMetadata": "test-metadata",
                    }
                ]
            },
            "response": {
                "issueTokens": False,
                "challengeName": "",
            },
        }

        self.test_context = {
            "function_name": "defineAuthChallenge",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:defineAuthChallenge:$LATEST",
            "memory_limit_in_mb": "128",
            "aws_request_id": "test-request-id",
            "log_group_name": "/aws/lambda/defineAuthChallenge",
            "log_stream_name": "test-log-stream",
        }

    def test_defineAuthChallenge_success(self):
        """Test successful defineAuthChallenge execution"""
        result = defineAuthChallenge.lambda_handler(self.test_event, self.test_context)

        # Check that the response structure is correct
        self.assertIn("response", result)
        self.assertIn("issueTokens", result["response"])
        self.assertTrue(result["response"]["issueTokens"])

    def test_defineAuthChallenge_invalid_event(self):
        """Test defineAuthChallenge with invalid event"""
        invalid_event = {}
        result = defineAuthChallenge.lambda_handler(invalid_event, self.test_context)

        # Should return error response structure
        self.assertIn("response", result)
        self.assertIn("challengeName", result["response"])
        self.assertEqual(result["response"]["challengeName"], "CUSTOM_CHALLENGE")


if __name__ == "__main__":
    unittest.main()
