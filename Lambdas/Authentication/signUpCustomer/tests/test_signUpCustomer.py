#!/usr/bin/env python3
"""
Unit tests for signUpCustomer Lambda function
"""

import unittest
import json
import sys
import os

# Add the function directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function module
import signUpCustomer

class TestSignupcustomer(unittest.TestCase):
    """Test cases for signUpCustomer function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'test': 'data'
            })
        }
        
        self.test_context = {
            'function_name': 'signUpCustomer',
            'function_version': '$LATEST',
            'invoked_function_arn': 'arn:aws:lambda:us-east-1:123456789012:function:signUpCustomer:$LATEST',
            'memory_limit_in_mb': '128',
            'aws_request_id': 'test-request-id',
            'log_group_name': '/aws/lambda/signUpCustomer',
            'log_stream_name': 'test-log-stream'
        }
    
    def test_signUpCustomer_success(self):
        """Test successful signUpCustomer execution"""
        result = signUpCustomer.signUpCustomer(self.test_event, self.test_context)
        
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('message', json.loads(result['body']))
    
    def test_signUpCustomer_invalid_event(self):
        """Test signUpCustomer with invalid event"""
        invalid_event = {}
        result = signUpCustomer.signUpCustomer(invalid_event, self.test_context)
        
        self.assertEqual(result['statusCode'], 200)  # Should still work with empty event

if __name__ == '__main__':
    unittest.main()
