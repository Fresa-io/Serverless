#!/usr/bin/env python3
"""
Unit tests for createAuthChallenge Lambda function
"""

import unittest
import json
import sys
import os

# Add the function directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function module
import createAuthChallenge


class TestCreateauthchallenge(unittest.TestCase):
    """Test cases for createAuthChallenge function"""

    def setUp(self):
        """Set up test fixtures"""
        # Cognito trigger event structure
        self.test_event = {
            "version": "1",
            "region": "us-east-1",
            "userPoolId": "us-east-1_TestPool",
            "userName": "test-user-123",
            "callerContext": {
                "awsSdkVersion": "aws-sdk-unknown-version",
                "clientId": "test-client-id",
            },
            "triggerSource": "CreateAuthChallenge_Authentication",
            "request": {
                "userAttributes": {
                    "email": "test@example.com",
                    "email_verified": "true",
                    "sub": "test-user-123",
                },
                "challengeName": "CUSTOM_CHALLENGE",
                "session": [
                    {
                        "challengeName": "CUSTOM_CHALLENGE",
                        "challengeResult": True,
                        "challengeMetadata": "test-metadata",
                    }
                ],
            },
            "response": {
                "publicChallengeParameters": {},
                "privateChallengeParameters": {},
                "challengeMetadata": "",
            },
        }

        self.test_context = {
            "function_name": "createAuthChallenge",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:createAuthChallenge:$LATEST",
            "memory_limit_in_mb": "128",
            "aws_request_id": "test-request-id",
            "log_group_name": "/aws/lambda/createAuthChallenge",
            "log_stream_name": "test-log-stream",
        }

    def test_createAuthChallenge_success(self):
        """Test successful createAuthChallenge execution"""
        result = createAuthChallenge.lambda_handler(self.test_event, self.test_context)

        # Check that the response structure is correct
        self.assertIn("response", result)
        self.assertIn("publicChallengeParameters", result["response"])
        self.assertIn("privateChallengeParameters", result["response"])
        self.assertIn("challengeMetadata", result["response"])
        self.assertEqual(result["version"], 1)

    def test_createAuthChallenge_invalid_event(self):
        """Test createAuthChallenge with invalid event"""
        invalid_event = {}
        result = createAuthChallenge.lambda_handler(invalid_event, self.test_context)

        # Should return error response structure
        self.assertIn("response", result)
        self.assertIn("challengeMetadata", result["response"])
        self.assertEqual(result["version"], 1)


if __name__ == "__main__":
    unittest.main()
