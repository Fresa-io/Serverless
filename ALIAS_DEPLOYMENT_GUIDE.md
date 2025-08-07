# Lambda Alias-Based Deployment Guide

This guide explains the new Lambda deployment workflow with proper alias management for STAGING and PROD environments.

## 🎯 Overview

The new deployment system provides:

- **🔒 Safe deployments** with alias-based versioning
- **🔄 Environment promotion** (STAGING → PROD)
- **🧪 Local testing** without affecting production
- **📋 GitHub Actions** for automated CI/CD with code review
- **🛡️ Zero-downtime deployments** with rollback capability
- **🎮 Single command** to start everything

## 🏗️ Architecture

### Lambda Aliases

Each Lambda function has two aliases:

- **`staging`** → Pre-production environment for validation
- **`prod`** → Production environment

### Development Workflow

```
Developer makes changes → Local testing → STAGING → PROD
```

**Note**: DEV environment is local-only, no alias needed. Developers test locally using the interactive menu.

## 🚀 Quick Start

### 1. Initial Setup

First, set up aliases for your existing Lambda functions:

```bash
# Build the enhanced container
docker build -t app .

# Setup aliases for all functions (STAGING and PROD only)
docker run --rm app setup-aliases QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

### 2. Start Deployment (That's It!)

The easiest way to work with the deployment system is using the single command:

```bash
# Start the interactive deployment system
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

This will show you a menu like this:

```
🚀 Lambda Deployment Interactive Menu
=====================================

Available Actions:
  1) 🔍 Show Deployment Status
  2) 🏷️  Setup Aliases
  3) 🧪 Test Function Locally
  4) 🧪 Run Unit Tests
  5) 📋 List Test Events
  6) 🚀 Deploy to STAGING
  7) 🚀 Deploy to PROD
  8) 🔄 Promote STAGING → PROD
  9) 💻 Interactive Shell
  10) ❌ Exit

Enter your choice (1-10):
```

When you select an action that requires a function (like testing or deploying), you'll see:

```
📋 Available Functions:
  1) tracer_import_results
  2) tracer_sqs_consumer
  3) All Functions
  4) 🔙 Back to Main Menu

Select function (1-4):
```

You can always go back to the main menu by selecting option 4 in the function selection.

## �� Local Testing (DEV Environment)

### Using Interactive Mode:

```bash
# Start interactive mode
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=

# Then select:
# 6) 🧪 Test Function Locally
# 7) 🧪 Run Unit Tests
# 8) 📋 List Test Events
```

## 📊 Monitoring and Status

### Check Deployment Status

```bash
# Using interactive mode
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
# Then select: 4) 🔍 Show Deployment Status
```

### List All Aliases

```bash
# List all aliases and versions
python lambda_alias_manager.py list
```

## 🔄 GitHub Actions Workflow

### Automated Deployment Pipeline

The GitHub Actions workflow provides:

1. **Code Quality Checks**

   - Linting with flake8
   - Code formatting with black
   - Unit tests for each function
   - Local function tests

2. **Environment Deployments**

   - **STAGING**: Manual approval required on `main` branch
   - **PROD**: Manual approval required via workflow dispatch

3. **Integration Tests**
   - Post-deployment validation
   - Function health checks

### Manual Deployment

You can trigger manual deployments via GitHub Actions:

1. Go to **Actions** → **Lambda Deployment Pipeline**
2. Click **Run workflow**
3. Select environment (staging or production) and function
4. Click **Run workflow**

## 🛠️ Development Workflow

### 1. Developer Workflow

```bash
# 1. Make changes to Lambda function code

# 2. Test locally (DEV environment) - Interactive Mode
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
# Select: 6) 🧪 Test Function Locally
# Select: 7) 🧪 Run Unit Tests

# 3. Commit and push to main branch
git add .
git commit -m "Add new feature to tracer_import_results"
git push origin main

# 4. GitHub Actions deploys to STAGING (requires approval)
# 5. Test in STAGING environment
# 6. Manually promote to PROD when ready (requires approval)
```

### 2. Emergency Rollback

If you need to rollback a deployment:

```bash
# Rollback to previous version
python lambda_alias_manager.py promote tracer_import_results <previous_version> PROD
```

## 📁 Project Structure

```
Serverless/
├── Lambdas/
│   └── Expansion/
│       ├── tracer_import_results/
│       │   ├── tracer_import_results.py
│       │   ├── test_events/
│       │   │   └── tracer_import_results_test_event.json
│       │   └── tests/
│       │       └── test_tracer_import_results.py
│       └── tracer_sqs_consumer/
│           ├── tracer_sqs_consumer.py
│           ├── test_events/
│           │   └── tracer_sqs_consumer_test_event.json
│           └── tests/
│               └── test_tracer_sqs_consumer.py
├── tests/
│   └── integration/              # Integration tests
├── .github/
│   ├── workflows/
│   │   └── deploy.yml           # GitHub Actions workflow
│   └── environments/            # Environment configurations
├── config.py                    # Configuration settings
├── lambda_alias_manager.py      # Alias management
├── deploy_with_aliases.py       # Enhanced deployment
├── local_test.py               # Local testing
└── entrypoint_enhanced.sh      # Enhanced Docker entrypoint
```

## 🔧 Configuration

### Environment Settings

Edit `config.py` to customize:

```python
# Lambda Function Names
LAMBDA_FUNCTION_NAMES = {
    "tracer_import_results": "your-actual-function-name",
    "tracer_sqs_consumer": "your-actual-function-name",
}

# Deployment Environments (STAGING and PROD only)
DEPLOYMENT_ENV = {
    "STAGING": {
        "alias": "staging",
        "description": "Staging environment",
        "auto_approve": False
    },
    "PROD": {
        "alias": "prod",
        "description": "Production environment",
        "auto_approve": False
    }
}
```

### GitHub Settings

1. **Repository Secrets**

   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

2. **Environment Protection Rules**
   - Configure required reviewers
   - Set deployment branch restrictions

## 🚨 Safety Features

### ✅ What's Protected

- **No accidental deletions**: Functions are never deleted, only updated
- **Version history**: All versions are preserved
- **Rollback capability**: Easy rollback to previous versions
- **Environment isolation**: STAGING and PROD are completely separate
- **Approval gates**: Both STAGING and PROD require manual approval
- **Local development**: DEV environment is local-only, no risk to production

### ⚠️ Best Practices

1. **Always test locally first**
2. **Use local testing for development**
3. **Validate in STAGING before PROD**
4. **Monitor deployments with status checks**
5. **Keep version history for rollbacks**

## 🔍 Troubleshooting

### Common Issues

**Function not found**

```bash
# Check if function exists
aws lambda list-functions --query 'Functions[?contains(FunctionName, `tracer`)].FunctionName'
```

**Alias not configured**

```bash
# Setup aliases
python lambda_alias_manager.py setup
```

**Deployment fails**

```bash
# Check function status
python deploy_with_aliases.py status
```

**Local test fails**

```bash
# Check function code
python local_test.py test tracer_import_results
```

**Unit tests fail**

```bash
# Run unit tests for specific function
python local_test.py test-unit tracer_import_results
```

### Getting Help

1. Check the deployment status: `python deploy_with_aliases.py status`
2. Review CloudWatch logs for function errors
3. Test locally to isolate issues
4. Check GitHub Actions logs for CI/CD issues

## 📈 Next Steps

### Advanced Features

1. **Blue/Green Deployments**: Implement traffic shifting
2. **Canary Deployments**: Gradual rollout with monitoring
3. **Automated Testing**: Integration tests for each environment
4. **Monitoring**: CloudWatch dashboards and alarms
5. **Cost Optimization**: Lambda provisioned concurrency

### Integration

1. **API Gateway**: Connect Lambda aliases to API endpoints
2. **EventBridge**: Trigger functions from events
3. **SQS**: Queue-based processing
4. **S3**: File processing workflows

---

## 🎉 Summary

This alias-based deployment system provides:

- **🔒 Safety**: No accidental production changes
- **🔄 Flexibility**: Easy environment promotion
- **🧪 Testing**: Local testing without affecting production
- **📋 Automation**: GitHub Actions CI/CD pipeline
- **🛡️ Reliability**: Version history and rollback capability
- **🎮 Single Command**: Just one command to start everything

**Usage**: Just run this one command!

```bash
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```
