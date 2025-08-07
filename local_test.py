#!/usr/bin/env python3
"""
Local Lambda Testing Script
Allows developers to test Lambda functions locally without affecting production
"""

import json
import sys
import os
import importlib.util
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from config import LAMBDA_FUNCTION_NAMES

class LocalLambdaTester:
    def __init__(self):
        """Initialize the local tester"""
        self.functions = LAMBDA_FUNCTION_NAMES
        
    def get_function_directory(self, function_key: str) -> Optional[str]:
        """Get the directory path for a specific function"""
        if function_key not in self.functions:
            print(f"❌ Function key {function_key} not found in configuration")
            return None
        
        # Find the function directory
        function_dir = None
        for root, dirs, files in os.walk("Lambdas"):
            for dir_name in dirs:
                if dir_name == function_key:
                    function_dir = os.path.join(root, dir_name)
                    break
            if function_dir:
                break
        
        if not function_dir:
            print(f"❌ Function directory not found for {function_key}")
            return None
        
        return function_dir
    
    def get_test_events_directory(self, function_key: str) -> str:
        """Get the test events directory for a specific function"""
        function_dir = self.get_function_directory(function_key)
        if not function_dir:
            return None
        
        test_events_dir = os.path.join(function_dir, "test_events")
        os.makedirs(test_events_dir, exist_ok=True)
        return test_events_dir
    
    def get_tests_directory(self, function_key: str) -> str:
        """Get the tests directory for a specific function"""
        function_dir = self.get_function_directory(function_key)
        if not function_dir:
            return None
        
        tests_dir = os.path.join(function_dir, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        return tests_dir
    
    def load_function_module(self, function_key: str) -> Optional[object]:
        """Load a Lambda function module for local testing"""
        function_dir = self.get_function_directory(function_key)
        if not function_dir:
            return None
        
        # Find the main function file
        main_file = None
        for file in os.listdir(function_dir):
            if file.endswith('.py') and not file.startswith('__'):
                main_file = os.path.join(function_dir, file)
                break
        
        if not main_file:
            print(f"❌ No main Python file found in {function_dir}")
            return None
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(function_key, main_file)
            module = importlib.util.module_from_spec(spec)
            
            # Add the function directory to Python path for imports
            sys.path.insert(0, function_dir)
            
            # Execute the module
            spec.loader.exec_module(module)
            
            print(f"✅ Loaded function module: {main_file}")
            return module
            
        except Exception as e:
            print(f"❌ Error loading function module: {e}")
            return None
    
    def find_handler_function(self, module: object, function_key: str) -> Optional[callable]:
        """Find the handler function in the module"""
        # Common handler function names
        handler_names = [
            f"{function_key}",
            f"{function_key}_handler",
            "handler",
            "lambda_handler",
            "main"
        ]
        
        for handler_name in handler_names:
            if hasattr(module, handler_name):
                handler = getattr(module, handler_name)
                if callable(handler):
                    print(f"✅ Found handler function: {handler_name}")
                    return handler
        
        print(f"❌ No handler function found in module")
        print(f"   Looked for: {', '.join(handler_names)}")
        return None
    
    def create_test_event(self, function_key: str, event_data: Dict[str, Any] = None) -> str:
        """Create a test event file in the function's test_events directory"""
        test_events_dir = self.get_test_events_directory(function_key)
        if not test_events_dir:
            return None
        
        if not event_data:
            # Default test event based on function type
            if function_key == "tracer_sqs_consumer":
                event_data = {
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
            else:
                # Default for HTTP-based functions
                event_data = {
                    "isBase64Encoded": False,
                    "body": json.dumps({
                        "trace_id": "test-trace-id-123",
                        "test": True
                    }),
                    "headers": {
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (compatible; TestBot/1.0)"
                    },
                    "requestContext": {
                        "identity": {
                            "sourceIp": "127.0.0.1",
                            "userAgent": "TestBot/1.0"
                        },
                        "http": {
                            "method": "POST",
                            "path": f"/{function_key}"
                        }
                    }
                }
        
        # Create test event file
        event_file = os.path.join(test_events_dir, f"{function_key}_test_event.json")
        with open(event_file, 'w') as f:
            json.dump(event_data, f, indent=2)
        
        print(f"✅ Created test event file: {event_file}")
        return event_file
    
    def load_test_event(self, event_file: str) -> Optional[Dict[str, Any]]:
        """Load a test event from file"""
        try:
            with open(event_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading test event: {e}")
            return None
    
    def test_function(self, function_key: str, event_file: str = None, context: Dict[str, Any] = None) -> bool:
        """Test a Lambda function locally"""
        print(f"🧪 Testing function: {function_key}")
        
        # Load the function module
        module = self.load_function_module(function_key)
        if not module:
            return False
        
        # Find the handler function
        handler = self.find_handler_function(module, function_key)
        if not handler:
            return False
        
        # Load or create test event
        if event_file and os.path.exists(event_file):
            event = self.load_test_event(event_file)
        else:
            event = self.load_test_event(self.create_test_event(function_key))
        
        if not event:
            return False
        
        # Create context if not provided
        if not context:
            context = {
                "function_name": self.functions[function_key],
                "function_version": "$LATEST",
                "invoked_function_arn": f"arn:aws:lambda:us-east-1:123456789012:function:{self.functions[function_key]}:$LATEST",
                "memory_limit_in_mb": "128",
                "aws_request_id": "test-request-id",
                "log_group_name": f"/aws/lambda/{self.functions[function_key]}",
                "log_stream_name": "test-log-stream",
                "remaining_time_in_millis": 30000
            }
        
        try:
            print(f"🚀 Invoking function with test event...")
            print(f"📄 Event: {json.dumps(event, indent=2)}")
            print("-" * 50)
            
            # Invoke the function
            result = handler(event, context)
            
            print("-" * 50)
            print(f"✅ Function executed successfully!")
            print(f"📤 Result: {json.dumps(result, indent=2, default=str)}")
            
            return True
            
        except Exception as e:
            print("-" * 50)
            print(f"❌ Function execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def list_test_events(self, function_key: str = None) -> List[str]:
        """List available test events for a function or all functions"""
        events = []
        
        if function_key:
            # List events for specific function
            test_events_dir = self.get_test_events_directory(function_key)
            if test_events_dir and os.path.exists(test_events_dir):
                for file in os.listdir(test_events_dir):
                    if file.endswith('.json'):
                        events.append(file)
        else:
            # List events for all functions
            for func_key in self.functions.keys():
                test_events_dir = self.get_test_events_directory(func_key)
                if test_events_dir and os.path.exists(test_events_dir):
                    for file in os.listdir(test_events_dir):
                        if file.endswith('.json'):
                            events.append(f"{func_key}/{file}")
        
        return events
    
    def run_function_tests(self, function_key: str) -> bool:
        """Run unit tests for a specific function"""
        tests_dir = self.get_tests_directory(function_key)
        if not tests_dir:
            print(f"❌ No tests directory found for {function_key}")
            return False
        
        # Check if pytest is available
        try:
            import pytest
        except ImportError:
            print("❌ pytest not available. Install with: pip install pytest")
            return False
        
        # Find test files
        test_files = []
        for file in os.listdir(tests_dir):
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(tests_dir, file))
        
        if not test_files:
            print(f"❌ No test files found in {tests_dir}")
            return False
        
        print(f"🧪 Running tests for {function_key}...")
        
        # Add the function directory to Python path
        function_dir = self.get_function_directory(function_key)
        if function_dir:
            sys.path.insert(0, function_dir)
        
        # Run tests
        try:
            import pytest
            result = pytest.main([tests_dir, "-v"])
            return result == 0
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def create_custom_test_event(self, function_key: str) -> str:
        """Create a custom test event interactively"""
        print(f"📝 Creating custom test event for {function_key}")
        print("Enter the test event JSON (press Ctrl+D when done):")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        event_json = '\n'.join(lines)
        
        try:
            event_data = json.loads(event_json)
            return self.create_test_event(function_key, event_data)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return None

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("🧪 Local Lambda Tester")
        print("")
        print("Usage:")
        print("  python local_test.py test <function_key> [event_file]")
        print("  python local_test.py test-unit <function_key>")
        print("  python local_test.py create-event <function_key>")
        print("  python local_test.py list-events [function_key]")
        print("")
        print("Function Keys:", ", ".join(LAMBDA_FUNCTION_NAMES.keys()))
        print("")
        print("Examples:")
        print("  python local_test.py test tracer_import_results")
        print("  python local_test.py test tracer_import_results tracer_import_results/test_events/custom_event.json")
        print("  python local_test.py test-unit tracer_import_results")
        print("  python local_test.py create-event tracer_import_results")
        print("  python local_test.py list-events")
        print("  python local_test.py list-events tracer_import_results")
        return
    
    command = sys.argv[1]
    tester = LocalLambdaTester()
    
    if command == "test":
        if len(sys.argv) < 3:
            print("❌ test command requires: function_key [event_file]")
            return
        
        function_key = sys.argv[2]
        event_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        tester.test_function(function_key, event_file)
    
    elif command == "test-unit":
        if len(sys.argv) != 3:
            print("❌ test-unit command requires: function_key")
            return
        
        function_key = sys.argv[2]
        tester.run_function_tests(function_key)
    
    elif command == "create-event":
        if len(sys.argv) != 3:
            print("❌ create-event command requires: function_key")
            return
        
        function_key = sys.argv[2]
        tester.create_custom_test_event(function_key)
    
    elif command == "list-events":
        function_key = sys.argv[2] if len(sys.argv) > 2 else None
        events = tester.list_test_events(function_key)
        if events:
            print("📋 Available test events:")
            for event in events:
                print(f"  - {event}")
        else:
            print("📋 No test events found")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 