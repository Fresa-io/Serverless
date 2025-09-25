# 🚀 Lambda Deployment System

A comprehensive Lambda deployment system with alias management, local testing, and interactive deployment workflows

## 🎯 The Magic: Multiple Ways to Create Lambda Functions

### 🔐 Local Development Setup

For your local development environment, I've created secure credential files:

- `local_credentials.sh` - Contains your actual AWS credentials (in .gitignore)
- `run_local.sh` - Quick script to run with your credentials
- `.gitignore` - Updated to prevent credential exposure

**Never commit `local_credentials.sh` to git!** It's automatically ignored.

**Option 1: Local Development (Your Environment)**

```bash
# Quick start with your local credentials
./run_local.sh
```

**Option 2: Updated CLI Script (Manual)**

```bash
./run_updated_cli.sh YOUR_BASE64_ENCODED_CREDENTIALS
```

**Option 2: Interactive Lambda Creator**

```bash
python3 create_lambda.py
```

**Option 3: Direct Command Line**

```bash
python3 scripts/add_lambda_function.py <function_name> <category>
```

These commands handle:

- ✅ Lambda function creation
- ✅ Local testing
- ✅ Unit tests
- ✅ Status checks
- ✅ Everything else

## 🎯 Your Deployment Flow

```
1. 🧪 Local Testing (DEV) → 2. 📋 Code Review → 3. 🚀 STAGING → 4. ✅ Approval → 5. 🚀 PROD
```

## 📋 Quick Setup (Multiple Options)

### Option 1: Updated CLI Script (Recommended)

```bash
# Use the updated CLI script that bypasses Docker registry issues
./run_updated_cli.sh <your-credentials>
```

### Option 2: Interactive Lambda Creator

```bash
# Use the interactive Python script
python3 create_lambda.py
```

### Option 3: Direct Command Line

```bash
# Create functions directly
python3 scripts/add_lambda_function.py <function_name> <category>
```

### Option 4: Docker (If Registry Issues Resolved)

```bash
# Build and run Docker (if registry authentication works)
docker build -t app .
docker run --rm -it app deploy <your-credentials>
```

**Note:** Docker registry authentication issues may prevent building. Use the alternative methods above.

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
docker run --rm -it app deploy YOUR_BASE64_ENCODED_CREDENTIALS
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

### Method 1: Updated CLI Script (Recommended)

1. **Run the updated CLI:**

   ```bash
   ./run_updated_cli.sh <your-credentials>
   ```

2. **Select option 5:** `🆕 Create New Lambda Function`

3. **Follow the prompts:**
   - Enter function name (e.g., `userLogin`, `processPayment`)
   - Choose category:
     - **Authentication** - login, signup, auth functions
     - **Processing** - data processing, file handling
     - **Communication** - email, SMS, notifications
     - **Analytics** - reporting, data analysis
     - **General** - default category
     - **Custom** - create your own category

### Method 2: Interactive Lambda Creator

```bash
python3 create_lambda.py
```

This provides a user-friendly interface that guides you through:

- Function name validation
- Category selection
- Confirmation before creation

### Method 3: Direct Command Line

```bash
python3 scripts/add_lambda_function.py <function_name> <category>
```

**Examples:**

```bash
python3 scripts/add_lambda_function.py userLogin Authentication
python3 scripts/add_lambda_function.py dataProcessor Processing
python3 scripts/add_lambda_function.py sendNotification Communication
```

### What Gets Created

Your function is automatically:

- ✅ Created with proper folder structure
- ✅ Added to configuration files
- ✅ Ready for local testing
- ✅ Available in all menus instantly
- ✅ **Ready for CI/CD deployment when pushed to GitHub**

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
# 1. Create function using any method:
./run_updated_cli.sh <credentials>  # Option 5: Create New Lambda Function
# OR
python3 create_lambda.py
# OR
python3 scripts/add_lambda_function.py myFunction CategoryName

# 2. Test locally
./run_updated_cli.sh <credentials>  # Option 2: Test Function Locally
# OR
python3 scripts/local_test.py test <function_name>

# 3. Create feature branch and deploy via Pull Request
git checkout -b feature/my-new-function
git add .
git commit -m "Add new function"
git push origin feature/my-new-function
# ↳ Create PR → Triggers validation → Manual review → Merge to main
# ↳ Merge triggers automatic STAGING deployment
# ↳ Manual promotion to PROD via GitHub Actions
```

## 🛡️ Safety Features

### What's Protected:

- ✅ **No direct commits to main**: Branch protection prevents accidents
- ✅ **Pull Request workflow**: All changes require review and approval
- ✅ **Automated testing**: PR validation runs before merge
- ✅ **Smart deployments**: Only deploys when Lambda code actually changes
- ✅ **Efficient CI/CD**: Documentation changes don't trigger deployments
- ✅ **No accidental deletions**: Functions are never deleted
- ✅ **Version history**: All versions are preserved
- ✅ **Rollback capability**: Easy rollback to previous versions
- ✅ **Environment isolation**: STAGING and PROD are separate
- ✅ **Approval gates**: Production requires manual approval
- ✅ **Local development**: DEV environment is local-only

### Security Workflow:

1. **Feature Branch** → Create isolated branch for changes
2. **Pull Request** → Triggers automated validation (testing, linting, security)
3. **Manual Review** → Human approval required before merge
4. **Merge to Main** → Triggers automatic STAGING deployment
5. **Production** → Manual approval required for PROD deployment

### Smart Deployment Logic:

#### **What Triggers Deployment:**

- Changes to Lambda function code (`Lambdas/**`)
- Changes to deployment scripts (`scripts/**`, `utils/**`)
- Changes to infrastructure (`cdk/**`, `config.py`, `app.py`)
- Changes to dependencies (`requirements.txt`)
- Changes to workflows (`.github/workflows/**`)

#### **What Skips Deployment:**

- Documentation changes (`**.md`)
- README updates
- Dockerfile modifications
- .gitignore changes
- Non-functional file updates

#### **Additional Protection:**

- Even when deployment runs, individual Lambda functions are only updated if their **code SHA256 hash changed**
- This prevents unnecessary version bumps when only dependencies or infrastructure change

### Best Practices:

1. **Always create feature branches**
2. **Test locally first**
3. **Write meaningful commit messages**
4. **Use staging for validation**
5. **Monitor deployments**
6. **Keep version history**
7. **Group related changes** (code + docs) in single PRs when appropriate

## 🚨 Troubleshooting

### Common Issues:

**1. Function not found**
**2. Aliases not configured**
**3. Local testing fails**

```bash
# Use the updated CLI script
./run_updated_cli.sh <your-credentials>
# OR use the interactive creator
python3 create_lambda.py
# OR use direct command line
python3 scripts/add_lambda_function.py <function_name> <category>
```

**4. GitHub Actions failing**

- Check repository secrets are configured
- See [GitHub Actions Setup Guide](.github/SETUP.md) for detailed configuration

## ⚙️ GitHub Actions Setup (Required for CI/CD)

### Quick Setup:

1. **Configure Repository Secrets:**

   - Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**
   - Add: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

2. **Configure Branch Protection:**

   - Go to **Settings** → **Branches**
   - Add rule for `main` branch
   - Enable: "Require a pull request before merging"
   - Enable: "Require status checks to pass before merging"
   - Add required checks: `Validate Pull Request / validate-pr` and `Validate Pull Request / security-scan`

3. **Configure Environments:**

   - Go to **Settings** → **Environments**
   - Create: `production` environment (staging uses no protection)
   - Set production to require reviewers

4. **Done!** Your CI/CD pipeline is ready.

📋 **Full setup guides:**

- [GitHub Actions Setup](.github/SETUP.md)
- [Branch Protection Setup](.github/BRANCH_PROTECTION_SETUP.md)
- Verify AWS credentials have proper permissions
- Check workflow logs for specific errors

## 📊 Monitoring

### Check Deployment Status

```bash
# Use the updated CLI script
./run_updated_cli.sh <your-credentials>
# Then select: 1) 🔍 Show Deployment Status

# OR check status directly
python3 scripts/deploy_with_aliases.py status
```

## 🎉 Summary

Your deployment system provides:

- **🔒 Safety**: No accidental production changes
- **🔄 Flexibility**: Easy environment promotion
- **🧪 Testing**: Local testing without affecting production
- **📋 Automation**: GitHub Actions CI/CD pipeline
- **🛡️ Reliability**: Version history and rollback capability
- **🎮 Single Command**: Just one command to start everything

**Ready to start?** Choose your preferred method:

```bash
# Option 1: Updated CLI Script (Recommended)
./run_updated_cli.sh <your-credentials>

# Option 2: Interactive Lambda Creator
python3 create_lambda.py

# Option 3: Direct Command Line
python3 scripts/add_lambda_function.py <function_name> <category>
```
