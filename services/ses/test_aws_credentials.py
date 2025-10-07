#!/usr/bin/env python3
"""
Fresa AWS Credentials Tester
Based on the original test_aws_credentials.py script
"""

import boto3
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from utils.aws_utils import get_aws_account_info, print_aws_info


def test_aws_credentials():
    """Test if AWS credentials are working"""

    print("🍓 Fresa AWS Credentials Tester")
    print("=" * 40)

    print("Testing AWS credentials...")
    print(f"AWS_REGION environment variable: {os.environ.get('AWS_REGION', 'Not set')}")
    print(
        f"AWS_ACCESS_KEY_ID environment variable: {'Set' if os.environ.get('AWS_ACCESS_KEY_ID') else 'Not set'}"
    )
    print(
        f"AWS_SECRET_ACCESS_KEY environment variable: {'Set' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'Not set'}"
    )
    print()

    try:
        # Test STS (to get account info)
        sts_client = boto3.client("sts")
        identity = sts_client.get_caller_identity()
        print("✅ AWS credentials are working!")
        print(f"Account ID: {identity.get('Account')}")
        print(f"User ARN: {identity.get('Arn')}")
        print()

        # Test SES specifically
        ses_client = boto3.client(
            "ses", region_name=os.environ.get("AWS_REGION", "us-east-1")
        )
        templates = ses_client.list_templates()
        print("✅ SES access is working!")
        print(f"Found {len(templates.get('TemplatesMetadata', []))} templates")

        # List existing templates
        if templates.get("TemplatesMetadata"):
            print("\n📧 Existing SES Templates:")
            for template in templates["TemplatesMetadata"]:
                print(
                    f"   - {template['Name']} (Created: {template['CreatedTimestamp']})"
                )

        return True

    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        print()
        print("Common solutions:")
        print("1. Run: aws configure")
        print("2. Set environment variables:")
        print("   export AWS_ACCESS_KEY_ID=your_key_id")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   export AWS_DEFAULT_REGION=us-east-1")
        print("3. Check ~/.aws/credentials file")

        return False


def main():
    """Main function"""
    success = test_aws_credentials()

    if success:
        print("\n🎉 All AWS services are working correctly!")
    else:
        print("\n❌ AWS credentials test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

