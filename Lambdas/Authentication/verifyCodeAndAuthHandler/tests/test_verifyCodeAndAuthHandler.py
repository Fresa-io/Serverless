import unittest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path to import the Lambda function
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verifyCodeAndAuthHandler import lambda_handler, check_user_exists_in_cognito, validate_code_in_dynamodb


class TestVerifyCodeAndAuthHandler(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.valid_event = {
            'body': json.dumps({
                'email': 'test@example.com',
                'code': '123456'
            })
        }
        self.context = Mock()
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'COGNITO_CLIENT_ID': 'test-client-id',
            'COGNITO_USER_POOL_ID': 'test-user-pool',
            'DYNAMODB_TABLE_NAME': 'test-table',
            'CODE_EXPIRATION_MINUTES': '5'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
    
    def test_missing_email(self):
        """Test missing email in request"""
        event = {
            'body': json.dumps({
                'code': '123456'
            })
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['error'], 'Missing email or code')
    
    def test_missing_code(self):
        """Test missing code in request"""
        event = {
            'body': json.dumps({
                'email': 'test@example.com'
            })
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['error'], 'Missing email or code')
    
    def test_invalid_json(self):
        """Test invalid JSON in request body"""
        event = {
            'body': 'invalid json'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertIn('Invalid JSON', body['error'])
    
    @patch('verifyCodeAndAuthHandler.cognito')
    def test_check_user_exists_success(self, mock_cognito):
        """Test successful user existence check"""
        mock_cognito.admin_get_user.return_value = {'Username': 'test@example.com'}
        
        result = check_user_exists_in_cognito('test@example.com')
        
        self.assertTrue(result)
        mock_cognito.admin_get_user.assert_called_once()
    
    @patch('verifyCodeAndAuthHandler.cognito')
    def test_check_user_not_exists(self, mock_cognito):
        """Test user does not exist"""
        from botocore.exceptions import ClientError
        
        error = ClientError(
            {'Error': {'Code': 'UserNotFoundException'}}, 
            'AdminGetUser'
        )
        mock_cognito.admin_get_user.side_effect = error
        
        result = check_user_exists_in_cognito('test@example.com')
        
        self.assertFalse(result)
    
    @patch('verifyCodeAndAuthHandler.dynamodb')
    def test_validate_code_success(self, mock_dynamodb):
        """Test successful code validation"""
        import time
        
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        current_time = int(time.time())
        mock_table.get_item.return_value = {
            'Item': {
                'code': '123456',
                'lastRequestTime': current_time - 60  # 1 minute ago
            }
        }
        
        result = validate_code_in_dynamodb('test@example.com', '123456')
        
        self.assertTrue(result['valid'])
    
    @patch('verifyCodeAndAuthHandler.dynamodb')
    def test_validate_code_expired(self, mock_dynamodb):
        """Test expired code validation"""
        import time
        
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        current_time = int(time.time())
        mock_table.get_item.return_value = {
            'Item': {
                'code': '123456',
                'lastRequestTime': current_time - 400  # 6+ minutes ago (expired)
            }
        }
        
        result = validate_code_in_dynamodb('test@example.com', '123456')
        
        self.assertFalse(result['valid'])
        self.assertEqual(result['error'], 'Verification code has expired')
        self.assertEqual(result['status_code'], 401)
    
    @patch('verifyCodeAndAuthHandler.dynamodb')
    def test_validate_code_wrong_code(self, mock_dynamodb):
        """Test wrong code validation"""
        import time
        
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        current_time = int(time.time())
        mock_table.get_item.return_value = {
            'Item': {
                'code': '654321',  # Different code
                'lastRequestTime': current_time - 60
            }
        }
        
        result = validate_code_in_dynamodb('test@example.com', '123456')
        
        self.assertFalse(result['valid'])
        self.assertEqual(result['error'], 'Invalid code')
        self.assertEqual(result['status_code'], 401)


if __name__ == '__main__':
    unittest.main()
