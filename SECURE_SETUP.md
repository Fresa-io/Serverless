# 🔒 Secure Environment Setup Guide

## 🚨 **IMPORTANT: Security First!**

This project now uses **secure environment variable management** instead of hardcoded credentials. This ensures your AWS credentials are never exposed in your code or GitHub repository.

## 🚀 **Quick Setup**

### **Option 1: Automated Setup (Recommended)**

```bash
python3 setup_environment.py
```

This will:

- ✅ Create a `.env` file from the template
- ✅ Prompt you for your AWS credentials
- ✅ Test the credentials
- ✅ Configure everything securely

### **Option 2: Manual Setup**

1. **Copy the environment template:**

   ```bash
   cp env.example .env
   ```

2. **Edit the `.env` file with your credentials:**

   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Fill in your AWS credentials:**

   ```bash
   AWS_ACCESS_KEY_ID=your-actual-access-key
   AWS_SECRET_ACCESS_KEY=your-actual-secret-key
   AWS_REGION=us-east-1
   ```

4. **Test your setup:**
   ```bash
   python3 utils/config_loader.py
   ```

## 🔐 **Security Features**

### **✅ What's Protected:**

- ✅ **No hardcoded credentials** in any source files
- ✅ **`.env` file is gitignored** - never committed to GitHub
- ✅ **Environment variables** loaded securely at runtime
- ✅ **Template file** (`env.example`) is safe to commit

### **✅ What's Safe to Commit:**

- ✅ All Python source code
- ✅ `env.example` template file
- ✅ Configuration files
- ✅ Documentation

### **❌ What's Never Committed:**

- ❌ `.env` file (contains your actual credentials)
- ❌ Any files with hardcoded credentials
- ❌ Local credential files

## 🛠️ **Usage**

### **Running Scripts:**

All scripts now automatically load your credentials from the `.env` file:

```bash
# Deploy functions
python3 scripts/deploy_with_aliases.py deploy-all STAGING

# Verify deployment
python3 scripts/verify_deployment.py

# Manage environment variables
python3 manage_env_vars.py list
```

### **Environment Variables:**

Your `.env` file should contain:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# Lambda Configuration
COGNITO_CLIENT_ID=5st6t5kci95r53btoro9du83f3
COGNITO_USER_POOL_ID=us-east-1_aSNl9TDUl
DYNAMODB_TABLE_NAME=VerificationCodes
CODE_EXPIRATION_MINUTES=5
```

## 🔄 **For Team Members**

### **New Team Member Setup:**

1. Clone the repository
2. Run: `python3 setup_environment.py`
3. Enter their AWS credentials when prompted
4. Start using the project!

### **CI/CD Pipeline:**

For GitHub Actions or other CI/CD systems, set these as repository secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

## 🚨 **Troubleshooting**

### **"Missing required environment variables" Error:**

```bash
# Make sure .env file exists
ls -la .env

# If missing, create it
cp env.example .env
# Then edit .env with your credentials
```

### **"AWS credentials verification failed" Error:**

```bash
# Test your credentials manually
python3 utils/config_loader.py

# Check your .env file
cat .env
```

### **"No module named 'utils.config_loader'" Error:**

```bash
# Make sure you're in the project root directory
pwd
# Should show: /path/to/Serverless

# Run from project root
python3 setup_environment.py
```

## 📋 **File Structure**

```
Serverless/
├── .env                    # Your credentials (NEVER commit)
├── .env.example           # Template (safe to commit)
├── env.example            # Template (safe to commit)
├── setup_environment.py   # Setup script
├── utils/
│   └── config_loader.py   # Secure credential loader
└── scripts/
    ├── deploy_with_aliases.py
    ├── verify_deployment.py
    └── ...
```

## ✅ **Verification**

After setup, verify everything works:

```bash
# Test credentials
python3 utils/config_loader.py

# Test deployment verification
python3 scripts/verify_deployment.py

# Test lambda function
python3 test_verify_lambda.py
```

## 🎉 **You're Secure!**

Your AWS credentials are now:

- ✅ **Secure** - No hardcoded credentials
- ✅ **Flexible** - Easy to change environments
- ✅ **Team-friendly** - Each developer can use their own credentials
- ✅ **CI/CD ready** - Works with GitHub Actions and other pipelines
- ✅ **GitHub safe** - No credentials will be committed
