#!/usr/bin/env python3
"""
Simple script to manage environment variables for your Lambda functions
This helps you understand and manage environment variables across STAGING and PROD
"""

import boto3
import json
import sys
import os

def get_lambda_client():
    """Get Lambda client with credentials from environment"""
    from utils.config_loader import setup_aws_environment
    
    # Setup AWS credentials from environment variables
    setup_aws_environment()
    
    region = os.environ.get("AWS_REGION", "us-east-1")
    return boto3.client("lambda", region_name=region)

def list_current_env_vars():
    """List current environment variables for verifyCodeAndAuthHandler"""
    lambda_client = get_lambda_client()
    
    try:
        response = lambda_client.get_function_configuration(
            FunctionName="verifyCodeAndAuthHandler"
        )
        
        env_vars = response.get("Environment", {}).get("Variables", {})
        
        print("🔍 Current Environment Variables for verifyCodeAndAuthHandler:")
        print("=" * 60)
        for key, value in env_vars.items():
            print(f"  {key}: {value}")
        
        return env_vars
        
    except Exception as e:
        print(f"❌ Error getting environment variables: {e}")
        return {}

def check_aliases():
    """Check if aliases exist and their environment variables"""
    lambda_client = get_lambda_client()
    
    try:
        # Check STAGING alias
        print("\n🔍 Checking STAGING alias...")
        staging_response = lambda_client.get_function_configuration(
            FunctionName="verifyCodeAndAuthHandler:staging"
        )
        staging_env_vars = staging_response.get("Environment", {}).get("Variables", {})
        print("STAGING Environment Variables:")
        for key, value in staging_env_vars.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"⚠️  STAGING alias not found or error: {e}")
    
    try:
        # Check PROD alias
        print("\n🔍 Checking PROD alias...")
        prod_response = lambda_client.get_function_configuration(
            FunctionName="verifyCodeAndAuthHandler:prod"
        )
        prod_env_vars = prod_response.get("Environment", {}).get("Variables", {})
        print("PROD Environment Variables:")
        for key, value in prod_env_vars.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"⚠️  PROD alias not found or error: {e}")

def update_env_vars_for_environment(environment):
    """Update environment variables for a specific environment"""
    lambda_client = get_lambda_client()
    
    # Your current environment variables
    base_env_vars = {
        "COGNITO_CLIENT_ID": "5st6t5kci95r53btoro9du83f3",
        "COGNITO_USER_POOL_ID": "us-east-1_aSNl9TDUl",
        "DYNAMODB_TABLE_NAME": "VerificationCodes",
        "CODE_EXPIRATION_MINUTES": "5"
    }
    
    # Add environment-specific variables
    if environment.upper() == "STAGING":
        base_env_vars["ENVIRONMENT"] = "staging"
        base_env_vars["DEBUG"] = "true"
    elif environment.upper() == "PROD":
        base_env_vars["ENVIRONMENT"] = "production"
        base_env_vars["DEBUG"] = "false"
    
    try:
        lambda_client.update_function_configuration(
            FunctionName="verifyCodeAndAuthHandler",
            Environment={"Variables": base_env_vars}
        )
        print(f"✅ Updated environment variables for {environment}")
        return True
    except Exception as e:
        print(f"❌ Error updating environment variables: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Lambda Environment Variable Manager")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python manage_env_vars.py <command>")
        print("Commands:")
        print("  list     - List current environment variables")
        print("  check    - Check aliases and their variables")
        print("  update   - Update environment variables")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_current_env_vars()
        
    elif command == "check":
        list_current_env_vars()
        check_aliases()
        
    elif command == "update":
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_env_vars.py update <environment>")
            print("Environments: staging, prod")
            return
        
        environment = sys.argv[2]
        if update_env_vars_for_environment(environment):
            print(f"✅ Successfully updated environment variables for {environment}")
        else:
            print(f"❌ Failed to update environment variables for {environment}")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
