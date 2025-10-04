#!/usr/bin/env python3
"""
Secure Configuration Loader
Loads AWS credentials and configuration from environment variables
"""

import os
from typing import Dict, Optional
from pathlib import Path


def load_aws_credentials() -> Dict[str, str]:
    """
    Load AWS credentials from environment variables
    Returns a dictionary with AWS credentials
    """
    credentials = {}

    # Required AWS credentials
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]

    # Check if .env file exists and load it
    env_file = Path(".env")
    if env_file.exists():
        load_env_file(env_file)

    # Check for required environment variables
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        else:
            credentials[var] = value

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please set these environment variables or create a .env file")
        print("   You can copy env.example to .env and fill in your values")
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return credentials


def load_env_file(env_file: Path) -> None:
    """
    Load environment variables from .env file
    """
    try:
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip("\"'")
                    os.environ[key] = value
    except Exception as e:
        print(f"⚠️  Warning: Could not load .env file: {e}")


def get_lambda_config() -> Dict[str, str]:
    """
    Get Lambda function configuration
    """
    config = {}

    # Lambda-specific environment variables
    lambda_vars = [
        "COGNITO_CLIENT_ID",
        "COGNITO_USER_POOL_ID",
        "DYNAMODB_TABLE_NAME",
        "CODE_EXPIRATION_MINUTES",
    ]

    for var in lambda_vars:
        value = os.environ.get(var)
        if value:
            config[var] = value

    return config


def setup_aws_environment() -> None:
    """
    Setup AWS environment variables
    This function should be called at the start of any script that needs AWS access
    """
    try:
        credentials = load_aws_credentials()

        # Set environment variables for boto3
        for key, value in credentials.items():
            os.environ[key] = value

        print(f"✅ AWS credentials loaded successfully")
        print(f"   Region: {credentials.get('AWS_REGION', 'us-east-1')}")

    except ValueError as e:
        # Check if we're in a CI environment or dry-run mode
        if (
            os.environ.get("CI")
            or os.environ.get("GITHUB_ACTIONS")
            or os.environ.get("DRY_RUN")
        ):
            print(f"⚠️  Running in CI/dry-run mode - AWS credentials not required")
            print(f"   Skipping AWS credential validation")
            return

        print(f"❌ Configuration error: {e}")
        raise


def verify_aws_credentials() -> bool:
    """
    Verify that AWS credentials are working
    """
    try:
        import boto3

        sts_client = boto3.client("sts")
        identity = sts_client.get_caller_identity()

        print(f"✅ AWS credentials verified")
        print(f"   Account ID: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")

        return True

    except Exception as e:
        print(f"❌ AWS credentials verification failed: {e}")
        return False


if __name__ == "__main__":
    """Test the configuration loader"""
    try:
        setup_aws_environment()
        verify_aws_credentials()
        print("🎉 Configuration loader working correctly!")
    except Exception as e:
        print(f"❌ Configuration loader failed: {e}")
