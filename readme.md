# 🚀 Lambda Deployment System

A comprehensive Lambda deployment system with alias management, local testing, and interactive deployment workflows

## 🎯 The Magic: One Command Does Everything

**Just run this one command for everything:**

```bash
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

This single command handles:

- ✅ Local testing
- ✅ Unit tests
- ✅ Deployment to STAGING
- ✅ Deployment to PROD
- ✅ Status checks
- ✅ Everything else

## 🎯 Your Deployment Flow

```
1. 🧪 Local Testing (DEV) → 2. 📋 Code Review → 3. 🚀 STAGING → 4. ✅ Approval → 5. 🚀 PROD
```

## 📋 Quick Setup (2 Steps)

### Step 1: Build the Docker Image (One Time Setup)

```bash
docker build -t app .
```

### Step 2: That's It! You're Ready

Everything else is handled by the single command. The system will:

- ✅ Check AWS credentials automatically
- ✅ Setup aliases if needed
- ✅ Guide you through all options
- ✅ Handle all deployments

**Just run this one command for everything:**

```bash
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

## 📁 Project Structure

```
Serverless/
├── Lambdas/                          # Lambda functions organized by category
│   └── Authentication/               # Authentication functions
│       └── verifyCodeAndAuthHandler/ # Individual function folder
│           ├── verifyCodeAndAuthHandler.py  # Function code
│           ├── requirements.txt             # Function dependencies
│           └── tests/                       # Function-specific tests
│               └── test_verifyCodeAndAuthHandler.py
├── scripts/                          # Deployment and management scripts
│   ├── local_test.py                 # Local Lambda testing
│   ├── lambda_alias_manager.py       # Alias management
│   ├── deploy_with_aliases.py        # Deployment with aliases
│   └── add_lambda_function.py        # Add new Lambda functions
├── utils/                            # Utility scripts
│   └── encrypt_utils.py              # Credential encryption utilities
├── cdk/                              # CDK infrastructure code
│   └── cdk_stack.py                  # Main CDK stack
├── config.py                         # Configuration settings
├── app.py                           # CDK app entry point
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Container definition
└── README.md                        # This file
```

## 🎮 Interactive Menu

The interactive menu provides easy access to all deployment operations:

```
🚀 Lambda Deployment Interactive Menu
=====================================

Available Actions:
  1) 🔍 Show Deployment Status
  2) 🧪 Test Function Locally
  3) 🧪 Run Unit Tests
  4) 📋 List Test Events
  5) 🆕 Create New Lambda Function
  6) 💻 Interactive Shell
  7) ❌ Exit

Enter your choice (1-7):
```

## 🚀 Your Complete Workflow

### Phase 1: Local Development & Testing

```bash
# Start the interactive deployment system
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

**That's it!** The interactive menu focuses on development and testing:

- 🆕 **Create New Lambda Function** - Add new functions easily
- 🧪 **Test Function Locally** - Debug and validate your code
- 🧪 **Run Unit Tests** - Ensure code quality
- 📋 **List Test Events** - View available test data
- 🔍 **Show Deployment Status** - View current deployments
- 💻 **Interactive Shell** - Full CLI access

🚀 **All deployments happen automatically via GitHub Actions CI/CD!**

### Phase 2: Automated CI/CD Pipeline

When you're ready to deploy, simply commit and push:

```bash
# Commit your changes
git add .
git commit -m "Add new userLogin function"
git push origin main
```

When you push to `main`, GitHub Actions automatically:

1. **Code Quality Checks**
   - ✅ Linting with flake8
   - ✅ Code formatting with black
   - ✅ Unit tests for each function
   - ✅ Local function tests

2. **STAGING Deployment** (requires approval)
   - 🚀 Deploys to `staging` alias
   - ⏳ Waits for manual approval
   - ✅ Runs integration tests

### Phase 3: Production Deployment

1. **Test in STAGING**
   - Verify everything works in staging environment
   - Check logs and metrics in AWS Console

2. **Promote to PROD**
   - Go to **Actions** → **Lambda Deployment Pipeline**
   - Click **Run workflow**
   - Select environment: `production`
   - ⏳ Wait for approval
   - ✅ Deployed to production

## 🆕 Creating New Lambda Functions

### Easy Function Creation

The simplest way to add a new Lambda function is through the **interactive Docker menu**:

1. **Start the container:**
   ```bash
   docker run --rm -it app deploy <your-credentials>
   ```

2. **Select option 9:** `🆕 Create New Lambda Function`

3. **Follow the prompts:**
   - Enter function name (e.g., `userLogin`, `processPayment`)
   - Choose category:
     - **Authentication** - login, signup, auth functions
     - **Processing** - data processing, file handling
     - **Communication** - email, SMS, notifications
     - **Analytics** - reporting, data analysis
     - **General** - default category
     - **Custom** - create your own category

4. **Done!** Your function is automatically:
   - ✅ Created with proper folder structure
   - ✅ Added to configuration files
   - ✅ Ready for local testing
   - ✅ Available in all menus instantly
   - ✅ **Ready for CI/CD deployment when pushed to GitHub**

### Alternative: Command Line

You can also create functions directly via command line:

```bash
# Inside the container or locally:
python3 scripts/add_lambda_function.py myFunction CategoryName
```

### What Gets Created

When you create a new function, it automatically generates:

```
Lambdas/CategoryName/functionName/
├── functionName.py              # Your Lambda function code
├── requirements.txt             # Function-specific dependencies
├── tests/
│   └── test_functionName.py     # Unit tests
└── test_events/
    └── functionName_test_event.json # Test event data
```

### Complete Development Workflow

```bash
# 1. Create function via Docker menu
docker run --rm -it app deploy <credentials>  # Option 5: Create New Lambda Function

# 2. Test locally
# Option 2: Test Function Locally
# Option 3: Run Unit Tests

# 3. Deploy via GitHub Actions
git add .
git commit -m "Add new function"
git push origin main
# ↳ Automatically deploys to STAGING (with approval)
# ↳ Manual promotion to PROD via GitHub Actions
```

## 🛡️ Safety Features

### What's Protected:

- ✅ **No accidental deletions**: Functions are never deleted
- ✅ **Version history**: All versions are preserved
- ✅ **Rollback capability**: Easy rollback to previous versions
- ✅ **Environment isolation**: STAGING and PROD are separate
- ✅ **Approval gates**: Both environments require manual approval
- ✅ **Local development**: DEV environment is local-only

### Best Practices:

1. **Always test locally first**
2. **Use staging for validation**
3. **Monitor deployments**
4. **Keep version history**

## 🚨 Troubleshooting

### Common Issues:

**1. Function not found**
**2. Aliases not configured**
**3. Local testing fails**

```bash
# Just run the single command - it handles everything
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

**4. GitHub Actions failing**

- Check repository secrets are configured
- See [GitHub Actions Setup Guide](../.github/SETUP.md) for detailed configuration

## ⚙️ GitHub Actions Setup (Required for CI/CD)

### Quick Setup:

1. **Configure Repository Secrets:**
   - Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**
   - Add: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

2. **Configure Environments:**
   - Go to **Settings** → **Environments**
   - Create: `staging` and `production` environments
   - Set production to require reviewers

3. **Done!** Your CI/CD pipeline is ready.

📋 **Full setup guide:** [.github/SETUP.md](../.github/SETUP.md)
- Verify AWS credentials have proper permissions
- Check workflow logs for specific errors

## 📊 Monitoring

### Check Deployment Status

```bash
# Just run the single command
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
# Then select: 1) 🔍 Show Deployment Status
```

## 🎉 Summary

Your deployment system provides:

- **🔒 Safety**: No accidental production changes
- **🔄 Flexibility**: Easy environment promotion
- **🧪 Testing**: Local testing without affecting production
- **📋 Automation**: GitHub Actions CI/CD pipeline
- **🛡️ Reliability**: Version history and rollback capability
- **🎮 Single Command**: Just one command to start everything

**Ready to start?** Run this command:

```bash
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```
