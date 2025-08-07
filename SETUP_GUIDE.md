# 🚀 Complete Setup Guide for Your Lambda Deployment Flow

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

The system will automatically:

- ✅ Setup `staging` and `prod` aliases for both functions
- ✅ Check AWS credentials
- ✅ Guide you through all options

### Step 3: Configure GitHub (For CI/CD)

In your GitHub repository (`https://github.com/t2modus/Serverless`):

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:

   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

3. Go to **Settings** → **Environments**
4. Create two environments:
   - **staging**: Add protection rules (optional)
   - **production**: Add protection rules (required)

## 🚀 Your Complete Workflow

### Phase 1: Local Development & Testing

```bash
# Start the interactive deployment system
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

**That's it!** The interactive menu will show you all options:

- 🧪 Test Function Locally
- 🧪 Run Unit Tests
- 📋 List Test Events
- 🚀 Deploy to STAGING
- 🚀 Deploy to PROD
- And more...

### Phase 2: Code Review & Push

```bash
# Commit your changes
git add .
git commit -m "Add new feature to tracer_import_results"
git push origin main
```

### Phase 3: Automated CI/CD Pipeline

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

### Phase 4: Production Deployment

1. **Test in STAGING**

   - Verify everything works in staging environment
   - Check logs and metrics

2. **Promote to PROD**
   - Go to **Actions** → **Lambda Deployment Pipeline**
   - Click **Run workflow**
   - Select:
     - Environment: `production`
     - Function: (leave empty for all functions)
   - Click **Run workflow**
   - ⏳ Wait for approval
   - ✅ Deployed to production

## 🔧 Configuration Files

### config.py (Already Updated)

```python
LAMBDA_FUNCTION_NAMES = {
    "tracer_import_results": "tracer_import_results",
    "tracer_sqs_consumer": "tracer_sqs_consumer",
}
```

### GitHub Actions (.github/workflows/deploy.yml)

- ✅ Already configured
- ✅ Handles staging and production deployments
- ✅ Requires manual approvals

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

```bash
# Just run the single command - it handles everything
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

**2. Aliases not configured**

```bash
# Just run the single command - it handles everything
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

**3. GitHub Actions failing**

- Check repository secrets are configured
- Verify AWS credentials have proper permissions
- Check workflow logs for specific errors

**4. Local testing fails**

```bash
# Just run the single command - it handles everything
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

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
