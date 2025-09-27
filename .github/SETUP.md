# GitHub Actions Setup Guide

## 🚀 Quick Setup (Required for CI/CD)

### 1. Configure Repository Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

Add these repository secrets:

```
AWS_ACCESS_KEY_ID = your-aws-access-key-id
AWS_SECRET_ACCESS_KEY = your-aws-secret-access-key
```

### 2. Configure Environments (Recommended)

Go to your GitHub repository → **Settings** → **Environments**

Create two environments:

- **staging** (with protection rules if desired)
- **production** (with required reviewers for approval)

### 3. That's It!

Your CI/CD pipeline is now ready. The workflow will trigger:

- **Automatically on push to main** → STAGING deployment
- **Manually via workflow dispatch** → PRODUCTION deployment

## 🎯 How It Works

### Automatic Triggers (Push to main):

```
Code Quality → Unit Tests → STAGING Deployment → Integration Tests
```

### Manual Triggers (Workflow Dispatch):

```
GitHub Actions → Run workflow → Select "production" → Deploy to PROD
```

## 🛡️ Security Features

- ✅ **Environment Protection**: Production requires manual approval
- ✅ **AWS Credentials**: Stored as encrypted secrets
- ✅ **Code Quality Gates**: Must pass before deployment
- ✅ **Integration Tests**: Verify staging before production

## 📋 Workflow Features

### Code Quality Checks:

- **Black** code formatting
- **Flake8** linting
- **Unit tests** for each function
- **Local function tests**

### Deployment:

- **Dynamic function discovery** (no hardcoded lists)
- **Alias management** (STAGING/PROD)
- **Status monitoring**
- **Rollback capability**

### Integration:

- **AWS CDK** deployment
- **Lambda aliases** for environment isolation
- **Automatic test execution**

## 🎮 Usage

### Deploy to STAGING (Automatic):

```bash
git add .
git commit -m "Add new feature"
git push origin main
# ↳ Automatically deploys to STAGING
```

### Deploy to PRODUCTION (Manual):

1. Go to **Actions** tab in GitHub
2. Click **Lambda Deployment Pipeline**
3. Click **Run workflow**
4. Select **production**
5. Click **Run workflow**
6. ✅ Requires approval in production environment

## 🚨 Troubleshooting

### Common Issues:

**1. Workflow fails with AWS credentials**

- Check that `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set in repository secrets
- Verify AWS permissions for Lambda, CDK deployment

**2. Environment protection rules**

- Make sure "production" environment exists in repository settings
- Configure required reviewers if needed

**3. Function not found**

- Verify function exists in `config.py`
- Check that function structure matches expected format

### Debug Commands:

```bash
# Check deployment status
cd Serverless
python scripts/deploy_with_aliases.py status

# List functions
python utils/function_discovery.py list

# Test locally
python scripts/local_test.py test <function_name>
```
