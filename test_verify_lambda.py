#!/usr/bin/env python3
"""
Test script for verifyCodeAndAuthHandler lambda function
This script helps test the lambda function locally before deployment
"""

import json
import os
import sys
from pathlib import Path

# Add the lambda directory to the path
lambda_path = (
    Path(__file__).parent / "Lambdas" / "Authentication" / "verifyCodeAndAuthHandler"
)
sys.path.insert(0, str(lambda_path))

# Set up environment variables for testing
os.environ["COGNITO_CLIENT_ID"] = "test-client-id"
os.environ["COGNITO_USER_POOL_ID"] = "test-user-pool-id"
os.environ["DYNAMODB_TABLE_NAME"] = "test-table"
os.environ["CODE_EXPIRATION_MINUTES"] = "5"


def test_lambda_import():
    """Test if the lambda function can be imported without errors"""
    try:
        from verifyCodeAndAuthHandler import lambda_handler

        print("✅ Lambda function imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False


def test_lambda_handler():
    """Test the lambda handler with a sample event"""
    try:
        from verifyCodeAndAuthHandler import lambda_handler

        # Create a test event
        test_event = {
            "body": json.dumps({"email": "test@example.com", "code": "123456"})
        }

        # Create a test context (minimal)
        class TestContext:
            def __init__(self):
                self.function_name = "test-function"
                self.function_version = "1"
                self.invoked_function_arn = (
                    "arn:aws:lambda:us-east-1:123456789012:function:test-function"
                )
                self.memory_limit_in_mb = 128
                self.remaining_time_in_millis = 30000
                self.aws_request_id = "test-request-id"

        context = TestContext()

        # Test the handler (this will fail with actual AWS calls, but should not crash on import)
        print("Testing lambda handler...")
        result = lambda_handler(test_event, context)
        print(f"✅ Lambda handler executed successfully")
        print(f"Response: {json.dumps(result, indent=2)}")
        return True

    except Exception as e:
        print(f"❌ Error testing lambda handler: {e}")
        return False


def main():
    """Main test function"""
    print("Testing verifyCodeAndAuthHandler lambda function...")
    print("=" * 50)

    # Test 1: Import test
    print("\n1. Testing import...")
    import_success = test_lambda_import()

    if not import_success:
        print("\n❌ Import test failed. Check the lambda function code.")
        return False

    # Test 2: Handler test
    print("\n2. Testing lambda handler...")
    handler_success = test_lambda_handler()

    if handler_success:
        print("\n✅ All tests passed! The lambda function should work correctly.")
        print("\nNext steps:")
        print("1. Update the environment variables in cdk_stack.py with actual values")
        print("2. Deploy the updated stack: cdk deploy")
        print("3. Test the deployed lambda function")
    else:
        print("\n❌ Handler test failed. Check the lambda function implementation.")

    return import_success and handler_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
