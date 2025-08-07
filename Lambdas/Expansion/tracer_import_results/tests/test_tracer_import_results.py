"""
Unit tests for tracer_import_results Lambda function
"""

import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add the function directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function module
import tracer_import_results


class TestTracerImportResults:
    def setup_method(self):
        """Setup test fixtures"""
        self.test_event = {
            "isBase64Encoded": False,
            "body": json.dumps({
                "trace_id": "test-trace-id-123",
                "test": True
            }),
            "headers": {
                "Content-Type": "application/json"
            },
            "requestContext": {
                "identity": {
                    "sourceIp": "127.0.0.1"
                }
            }
        }
        
        self.test_context = {
            "function_name": "tracer-import-results-function",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:tracer-import-results-function:$LATEST",
            "memory_limit_in_mb": "128",
            "aws_request_id": "test-request-id",
            "log_group_name": "/aws/lambda/tracer-import-results-function",
            "log_stream_name": "test-log-stream",
            "remaining_time_in_millis": 30000
        }
    
    @patch('tracer_import_results.api_tracker')
    @patch('tracer_import_results.check_tracer_import_status')
    def test_tracer_import_results_success(self, mock_check_status, mock_api_tracker):
        """Test successful tracer_import_results execution"""
        # Mock the check_tracer_import_status to return success
        mock_check_status.return_value = (True, {
            'code': 1,
            'trace_id': 'test-trace-id-123',
            'import_file_name': 'test.csv',
            'processed_file_status': 'Complete'
        })
        
        # Call the function
        result = tracer_import_results.tracer_import_results(self.test_event, self.test_context)
        
        # Verify the result
        assert result['statusCode'] == 200
        assert 'body' in result
        assert 'headers' in result
        
        # Parse the response body
        response_body = json.loads(result['body'])
        assert response_body['code'] == 1
        assert response_body['trace_id'] == 'test-trace-id-123'
        
        # Verify API tracker was called
        mock_api_tracker.assert_called_once()
    
    @patch('tracer_import_results.api_tracker')
    @patch('tracer_import_results.check_tracer_import_status')
    @patch('tracer_import_results.tracer_import_status')
    def test_tracer_import_results_not_found_then_success(self, mock_import_status, mock_check_status, mock_api_tracker):
        """Test when check_tracer_import_status fails but tracer_import_status succeeds"""
        # Mock check_tracer_import_status to return False (not found)
        mock_check_status.return_value = (False, {})
        
        # Mock tracer_import_status to return success
        mock_import_status.return_value = (True, {
            'code': 1,
            'trace_id': 'test-trace-id-123',
            'import_file_name': 'test.csv',
            'processed_file_status': 'Complete'
        })
        
        # Call the function
        result = tracer_import_results.tracer_import_results(self.test_event, self.test_context)
        
        # Verify the result
        assert result['statusCode'] == 200
        assert 'body' in result
        
        # Parse the response body
        response_body = json.loads(result['body'])
        assert response_body['code'] == 1
        
        # Verify both functions were called
        mock_check_status.assert_called_once()
        mock_import_status.assert_called_once()
    
    @patch('tracer_import_results.api_tracker')
    @patch('tracer_import_results.check_tracer_import_status')
    @patch('tracer_import_results.tracer_import_status')
    def test_tracer_import_results_processing_incomplete(self, mock_import_status, mock_check_status, mock_api_tracker):
        """Test when processing is incomplete"""
        # Mock both functions to return incomplete status
        mock_check_status.return_value = (False, {})
        mock_import_status.return_value = (False, {
            'code': -1,
            'trace_id': 'test-trace-id-123',
            'processed_file_status': 'Waiting to finish import process.!'
        })
        
        # Call the function
        result = tracer_import_results.tracer_import_results(self.test_event, self.test_context)
        
        # Verify the result
        assert result['statusCode'] == 200
        assert 'body' in result
        
        # Parse the response body
        response_body = json.loads(result['body'])
        assert response_body['code'] == -1
        assert 'Waiting to finish import process' in response_body['processed_file_status']
    
    def test_tracer_import_results_invalid_payload(self):
        """Test with invalid payload (missing trace_id)"""
        invalid_event = {
            "isBase64Encoded": False,
            "body": json.dumps({
                "invalid_field": "test"
            }),
            "headers": {
                "Content-Type": "application/json"
            },
            "requestContext": {
                "identity": {
                    "sourceIp": "127.0.0.1"
                }
            }
        }
        
        # Call the function
        result = tracer_import_results.tracer_import_results(invalid_event, self.test_context)
        
        # Verify the result
        assert result['statusCode'] == 200
        assert 'body' in result
        
        # Parse the response body
        response_body = json.loads(result['body'])
        assert response_body['code'] == -1
        assert 'Invalid Payload' in response_body['message']
    
    def test_tracer_import_results_base64_encoded(self):
        """Test with base64 encoded payload"""
        import base64
        
        payload = {
            "trace_id": "test-trace-id-123",
            "test": True
        }
        
        base64_event = {
            "isBase64Encoded": True,
            "body": base64.b64encode(json.dumps(payload).encode()).decode(),
            "headers": {
                "Content-Type": "application/json"
            },
            "requestContext": {
                "identity": {
                    "sourceIp": "127.0.0.1"
                }
            }
        }
        
        with patch('tracer_import_results.api_tracker'), \
             patch('tracer_import_results.check_tracer_import_status') as mock_check_status:
            
            mock_check_status.return_value = (True, {
                'code': 1,
                'trace_id': 'test-trace-id-123'
            })
            
            # Call the function
            result = tracer_import_results.tracer_import_results(base64_event, self.test_context)
            
            # Verify the result
            assert result['statusCode'] == 200
            assert 'body' in result
    
    def test_response_headers(self):
        """Test that response headers are set correctly"""
        with patch('tracer_import_results.api_tracker'), \
             patch('tracer_import_results.check_tracer_import_status') as mock_check_status:
            
            mock_check_status.return_value = (True, {
                'code': 1,
                'trace_id': 'test-trace-id-123'
            })
            
            # Call the function
            result = tracer_import_results.tracer_import_results(self.test_event, self.test_context)
            
            # Verify headers
            assert 'headers' in result
            assert result['headers']['Content-Type'] == 'application/json'
            assert result['headers']['Access-Control-Allow-Origin'] == '*'


if __name__ == "__main__":
    pytest.main([__file__]) 