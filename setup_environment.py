#!/usr/bin/env python3
"""
Environment Setup Script
Helps configure AWS credentials and environment variables securely
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from template"""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ env.example file not found!")
        return False
    
    if env_file.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("✅ Keeping existing .env file")
            return True
    
    # Copy template to .env
    with open(env_example, 'r') as src, open(env_file, 'w') as dst:
        dst.write(src.read())
    
    print("✅ Created .env file from template")
    return True


def setup_aws_credentials():
    """Interactive setup of AWS credentials"""
    print("\n🔧 AWS Credentials Setup")
    print("=" * 40)
    
    # Get AWS credentials from user
    access_key = input("Enter your AWS Access Key ID: ").strip()
    secret_key = input("Enter your AWS Secret Access Key: ").strip()
    region = input("Enter AWS Region (default: us-east-1): ").strip() or "us-east-1"
    
    if not access_key or not secret_key:
        print("❌ AWS credentials are required!")
        return False
    
    # Update .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Run setup first.")
        return False
    
    # Read current .env content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace placeholder values
    content = content.replace("your-aws-access-key-id", access_key)
    content = content.replace("your-aws-secret-access-key", secret_key)
    content = content.replace("us-east-1", region)
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ AWS credentials configured in .env file")
    return True


def test_credentials():
    """Test AWS credentials"""
    print("\n🧪 Testing AWS Credentials")
    print("=" * 40)
    
    try:
        from utils.config_loader import setup_aws_environment, verify_aws_credentials
        
        setup_aws_environment()
        if verify_aws_credentials():
            print("✅ AWS credentials are working correctly!")
            return True
        else:
            print("❌ AWS credentials test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing credentials: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Serverless Project Environment Setup")
    print("=" * 50)
    
    # Step 1: Create .env file
    print("\n1️⃣ Creating .env file...")
    if not create_env_file():
        print("❌ Failed to create .env file")
        return False
    
    # Step 2: Setup AWS credentials
    print("\n2️⃣ Setting up AWS credentials...")
    if not setup_aws_credentials():
        print("❌ Failed to setup AWS credentials")
        return False
    
    # Step 3: Test credentials
    print("\n3️⃣ Testing AWS credentials...")
    if not test_credentials():
        print("❌ AWS credentials test failed")
        print("💡 Please check your credentials and try again")
        return False
    
    print("\n🎉 Environment setup complete!")
    print("\n📋 Next steps:")
    print("   1. Your .env file contains your AWS credentials")
    print("   2. All scripts will now use these credentials securely")
    print("   3. You can safely commit your code to GitHub")
    print("   4. Run: python3 scripts/verify_deployment.py")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
