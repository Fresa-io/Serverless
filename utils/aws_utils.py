#!/usr/bin/env python3
"""
AWS Utilities
Helper functions for AWS account and region detection
"""

import boto3
import os
from typing import Dict, Optional


def get_aws_account_info() -> Dict[str, str]:
    """
    Get AWS account information from current credentials
    Returns account ID, region, and user ARN
    """
    try:
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        
        # Get region from environment or default
        region = (
            os.environ.get('AWS_REGION') or 
            os.environ.get('CDK_DEFAULT_REGION') or 
            'us-east-1'
        )
        
        return {
            'account_id': identity['Account'],
            'region': region,
            'user_arn': identity['Arn'],
            'user_id': identity['UserId']
        }
    except Exception as e:
        raise Exception(f"Failed to get AWS account info: {e}")


def get_aws_region() -> str:
    """Get AWS region from environment variables or default"""
    return (
        os.environ.get('AWS_REGION') or 
        os.environ.get('CDK_DEFAULT_REGION') or 
        'us-east-1'
    )


def get_lambda_execution_role_arn() -> str:
    """
    Get the Lambda execution role ARN for the current account
    """
    account_info = get_aws_account_info()
    return f"arn:aws:iam::{account_info['account_id']}:role/lambda_basic_execution"


def verify_aws_credentials() -> bool:
    """
    Verify that AWS credentials are working
    """
    try:
        sts_client = boto3.client('sts')
        sts_client.get_caller_identity()
        return True
    except Exception:
        return False


def print_aws_info():
    """Print current AWS account information"""
    try:
        account_info = get_aws_account_info()
        print("🔍 Current AWS Configuration:")
        print(f"   Account ID: {account_info['account_id']}")
        print(f"   Region: {account_info['region']}")
        print(f"   User: {account_info['user_arn']}")
        print(f"   User ID: {account_info['user_id']}")
        return account_info
    except Exception as e:
        print(f"❌ Error getting AWS info: {e}")
        return None


if __name__ == "__main__":
    print_aws_info()
