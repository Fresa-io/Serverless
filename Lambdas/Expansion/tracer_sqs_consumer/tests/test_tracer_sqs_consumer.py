"""
Unit tests for tracer_sqs_consumer Lambda function
"""

import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add the function directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function module
import tracer_sqs_consumer


class TestTracerSqsConsumer:
    def setup_method(self):
        """Setup test fixtures"""
        self.test_event = {
            "Records": [
                {
                    "messageId": "test-message-id-123",
                    "receiptHandle": "test-receipt-handle",
                    "body": json.dumps({
                        "trace_id": "test-trace-id-456",
                        "action": "process",
                        "test": True
                    }),
                    "attributes": {
                        "ApproximateReceiveCount": "1",
                        "SentTimestamp": "1640995200000",
                        "SenderId": "test-sender-id",
                        "ApproximateFirstReceiveTimestamp": "1640995200000"
                    },
                    "messageAttributes": {
                        "test": {
                            "stringValue": "true",
                            "dataType": "String"
                        }
                    },
                    "md5OfBody": "test-md5-hash",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:test-queue",
                    "awsRegion": "us-east-1"
                }
            ]
        }
        
        self.test_context = {
            "function_name": "tracer-sqs-consumer-function",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:tracer-sqs-consumer-function:$LATEST",
            "memory_limit_in_mb": "128",
            "aws_request_id": "test-request-id",
            "log_group_name": "/aws/lambda/tracer-sqs-consumer-function",
            "log_stream_name": "test-log-stream",
            "remaining_time_in_millis": 30000
        }
    
    @patch('tracer_sqs_consumer.api_tracker')
    @patch('tracer_sqs_consumer.process_sqs_message')
    def test_tracer_sqs_consumer_success(self, mock_process_message, mock_api_tracker):
        """Test successful tracer_sqs_consumer execution"""
        # Mock the process_sqs_message to return success
        mock_process_message.return_value = {
            'status': 'success',
            'message': 'Message processed successfully',
            'trace_id': 'test-trace-id-456'
        }
        
        # Call the function
        result = tracer_sqs_consumer.tracer_sqs_consumer(self.test_event, self.test_context)
        
        # Verify the result
        assert result['statusCode'] == 200
        assert 'body' in result
        assert 'headers' in result
        
        # Parse the response body
        response_body = json.loads(result['body'])
        assert response_body['status'] == 'success'
        assert response_body['trace_id'] == 'test-trace-id-456'
        
        # Verify API tracker was called
        mock_api_tracker.assert_called_once()
        mock_process_message.assert_called_once()
    
    @patch('tracer_sqs_consumer.api_tracker')
    @patch('tracer_sqs_consumer.process_sqs_message')
    def test_tracer_sqs_consumer_processing_error(self, mock_process_message, mock_api_tracker):
        """Test when message processing fails"""
        # Mock the process_sqs_message to return error
        mock_process_message.return_value = {
            'status': 'error',
            'message': 'Failed to process message',
            'trace_id': 'test-trace-id-456'
        }
        
        # Call the function
        result = tracer_sqs_consumer.tracer_sqs_consumer(self.test_event, self.test_context)
        
        # Verify the result
        assert result['statusCode'] == 200
        assert 'body' in result
        
        # Parse the response body
        response_body = json.loads(result['body'])
        assert response_body['status'] == 'error'
        assert 'Failed to process message' in response_body['message']
    
    @patch('tracer_sqs_consumer.api_tracker')
    @patch('tracer_sqs_consumer.process_sqs_message')
    def test_tracer_sqs_consumer_exception(self, mock_process_message, mock_api_tracker):
        """Test when an exception occurs during processing"""
        # Mock the process_sqs_message to raise an exception
        mock_process_message.side_effect = Exception("Database connection failed")
        
        # Call the function
        result = tracer_sqs_consumer.tracer_sqs_consumer(self.test_event, self.test_context)
        
        # Verify the result
        assert result['statusCode'] == 500
        assert 'body' in result
        
        # Parse the response body
        response_body = json.loads(result['body'])
        assert response_body['status'] == 'error'
        assert 'Database connection failed' in response_body['message']
    
    def test_tracer_sqs_consumer_empty_records(self):
        """Test with empty Records array"""
        empty_event = {
            "Records": []
        }
        
        # Call the function
        result = tracer_sqs_consumer.tracer_sqs_consumer(empty_event, self.test_context)
        
        # Verify the result
        assert result['statusCode'] == 200
        assert 'body' in result
        
        # Parse the response body
        response_body = json.loads(result['body'])
        assert response_body['status'] == 'success'
        assert 'No messages to process' in response_body['message']
    
    def test_tracer_sqs_consumer_multiple_records(self):
        """Test with multiple SQS records"""
        multiple_records_event = {
            "Records": [
                {
                    "messageId": "test-message-id-1",
                    "body": json.dumps({"trace_id": "test-1", "action": "process"}),
                    "eventSource": "aws:sqs",
                    "awsRegion": "us-east-1"
                },
                {
                    "messageId": "test-message-id-2",
                    "body": json.dumps({"trace_id": "test-2", "action": "process"}),
                    "eventSource": "aws:sqs",
                    "awsRegion": "us-east-1"
                }
            ]
        }
        
        with patch('tracer_sqs_consumer.api_tracker'), \
             patch('tracer_sqs_consumer.process_sqs_message') as mock_process_message:
            
            mock_process_message.return_value = {
                'status': 'success',
                'message': 'Message processed successfully'
            }
            
            # Call the function
            result = tracer_sqs_consumer.tracer_sqs_consumer(multiple_records_event, self.test_context)
            
            # Verify the result
            assert result['statusCode'] == 200
            assert 'body' in result
            
            # Verify process_sqs_message was called for each record
            assert mock_process_message.call_count == 2
    
    def test_tracer_sqs_consumer_invalid_message_body(self):
        """Test with invalid message body (not JSON)"""
        invalid_event = {
            "Records": [
                {
                    "messageId": "test-message-id-123",
                    "body": "invalid-json-string",
                    "eventSource": "aws:sqs",
                    "awsRegion": "us-east-1"
                }
            ]
        }
        
        with patch('tracer_sqs_consumer.api_tracker'), \
             patch('tracer_sqs_consumer.process_sqs_message') as mock_process_message:
            
            mock_process_message.return_value = {
                'status': 'error',
                'message': 'Invalid JSON in message body'
            }
            
            # Call the function
            result = tracer_sqs_consumer.tracer_sqs_consumer(invalid_event, self.test_context)
            
            # Verify the result
            assert result['statusCode'] == 200
            assert 'body' in result
            
            # Parse the response body
            response_body = json.loads(result['body'])
            assert response_body['status'] == 'error'
    
    def test_response_headers(self):
        """Test that response headers are set correctly"""
        with patch('tracer_sqs_consumer.api_tracker'), \
             patch('tracer_sqs_consumer.process_sqs_message') as mock_process_message:
            
            mock_process_message.return_value = {
                'status': 'success',
                'message': 'Message processed successfully'
            }
            
            # Call the function
            result = tracer_sqs_consumer.tracer_sqs_consumer(self.test_event, self.test_context)
            
            # Verify headers
            assert 'headers' in result
            assert result['headers']['Content-Type'] == 'application/json'
            assert result['headers']['Access-Control-Allow-Origin'] == '*'
    
    def test_message_attributes_processing(self):
        """Test processing of message attributes"""
        event_with_attributes = {
            "Records": [
                {
                    "messageId": "test-message-id-123",
                    "body": json.dumps({
                        "trace_id": "test-trace-id-456",
                        "action": "process"
                    }),
                    "messageAttributes": {
                        "priority": {
                            "stringValue": "high",
                            "dataType": "String"
                        },
                        "retry_count": {
                            "stringValue": "3",
                            "dataType": "Number"
                        }
                    },
                    "eventSource": "aws:sqs",
                    "awsRegion": "us-east-1"
                }
            ]
        }
        
        with patch('tracer_sqs_consumer.api_tracker'), \
             patch('tracer_sqs_consumer.process_sqs_message') as mock_process_message:
            
            mock_process_message.return_value = {
                'status': 'success',
                'message': 'Message processed successfully',
                'attributes': {
                    'priority': 'high',
                    'retry_count': 3
                }
            }
            
            # Call the function
            result = tracer_sqs_consumer.tracer_sqs_consumer(event_with_attributes, self.test_context)
            
            # Verify the result
            assert result['statusCode'] == 200
            assert 'body' in result


if __name__ == "__main__":
    pytest.main([__file__]) 