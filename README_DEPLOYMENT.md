# 🚀 Multi-Account Lambda Deployment Guide

This project is designed to work with **any AWS account** without hardcoded credentials or account IDs. The system automatically detects your AWS account information from your credentials.

## 🔧 How It Works

### Dynamic Account Detection

- **Account ID:** Automatically detected from AWS credentials
- **Region:** Automatically detected from `AWS_REGION` environment variable
- **User:** Automatically detected from AWS credentials
- **Role ARNs:** Dynamically constructed using detected account ID

### No Hardcoded Values

- ❌ No hardcoded account IDs
- ❌ No hardcoded region values
- ❌ No hardcoded ARNs
- ✅ Everything is dynamically detected

## 🚀 Quick Start

### 1. Set Your AWS Credentials

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"  # or your preferred region
```

### 2. Verify Your Setup

```bash
python3 scripts/verify_deployment.py
```

This will show you:

- Your current AWS account ID
- Your current region
- Your current user
- Status of all Lambda functions

### 3. Deploy Functions

```bash
# Deploy all functions to STAGING
python3 scripts/deploy_with_aliases.py deploy-all STAGING

# Deploy all functions to PRODUCTION
python3 scripts/deploy_with_aliases.py deploy-all PROD
```

## 🔄 Using Different AWS Accounts

### Switch to Different Account

```bash
# Switch to different AWS account
export AWS_ACCESS_KEY_ID="different-access-key"
export AWS_SECRET_ACCESS_KEY="different-secret-key"
export AWS_REGION="us-west-2"  # different region

# Verify the switch
python3 scripts/verify_deployment.py
```

### Deploy to Multiple Accounts

```bash
# Account 1
export AWS_ACCESS_KEY_ID="account1-key"
export AWS_SECRET_ACCESS_KEY="account1-secret"
python3 scripts/deploy_with_aliases.py deploy-all STAGING

# Account 2
export AWS_ACCESS_KEY_ID="account2-key"
export AWS_SECRET_ACCESS_KEY="account2-secret"
python3 scripts/deploy_with_aliases.py deploy-all STAGING
```

## 🏗️ Architecture

### File Structure

```
Serverless/
├── config.py                 # Configuration (no hardcoded values)
├── utils/aws_utils.py        # AWS account detection utilities
├── scripts/
│   ├── deploy_with_aliases.py # Main deployment script
│   └── verify_deployment.py  # Verification script
├── cdk/
│   └── cdk_stack.py         # CDK stack (dynamic account detection)
└── Lambdas/                  # Lambda function source code
```

### Key Components

1. **`utils/aws_utils.py`** - Detects AWS account info dynamically
2. **`config.py`** - Configuration with auto-detection
3. **`scripts/deploy_with_aliases.py`** - Deployment with dynamic ARNs
4. **`cdk/cdk_stack.py`** - CDK stack with dynamic account detection

## 🔐 Security Features

### No Hardcoded Secrets

- ✅ All credentials come from environment variables
- ✅ Account IDs are auto-detected
- ✅ ARNs are dynamically constructed
- ✅ No sensitive data in code

### Multi-Account Support

- ✅ Works with any AWS account
- ✅ Easy account switching
- ✅ No code changes needed
- ✅ Same deployment process

## 🎯 Usage Examples

### Development Team

```bash
# Developer 1 (Account A)
export AWS_ACCESS_KEY_ID="dev1-key"
export AWS_SECRET_ACCESS_KEY="dev1-secret"
python3 scripts/deploy_with_aliases.py deploy-all STAGING

# Developer 2 (Account B)
export AWS_ACCESS_KEY_ID="dev2-key"
export AWS_SECRET_ACCESS_KEY="dev2-secret"
python3 scripts/deploy_with_aliases.py deploy-all STAGING
```

### CI/CD Pipeline

```yaml
# GitHub Actions
- name: Deploy to STAGING
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    AWS_REGION: us-east-1
  run: python3 scripts/deploy_with_aliases.py deploy-all STAGING
```

### Multi-Environment

```bash
# Staging environment
export AWS_ACCESS_KEY_ID="staging-key"
export AWS_SECRET_ACCESS_KEY="staging-secret"
python3 scripts/deploy_with_aliases.py deploy-all STAGING

# Production environment
export AWS_ACCESS_KEY_ID="prod-key"
export AWS_SECRET_ACCESS_KEY="prod-secret"
python3 scripts/deploy_with_aliases.py deploy-all PROD
```

## 🛠️ Troubleshooting

### Check Current Configuration

```bash
python3 utils/aws_utils.py
```

### Verify AWS Credentials

```bash
aws sts get-caller-identity
```

### Check Lambda Functions

```bash
python3 scripts/verify_deployment.py
```

## 📋 Requirements

- Python 3.9+
- AWS CLI configured or environment variables set
- Appropriate AWS permissions for Lambda operations

## 🎉 Benefits

1. **Portable** - Works with any AWS account
2. **Secure** - No hardcoded credentials
3. **Flexible** - Easy account switching
4. **Maintainable** - No account-specific code
5. **Scalable** - Works for teams and organizations

This design ensures your code can be used by anyone with their own AWS account without any modifications!
