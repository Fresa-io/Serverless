# 🚀 Quick Start Checklist

## ✅ Pre-Flight Checklist

### 1. Build Docker Image (One Time)

- [ ] Build: `docker build -t app .`

### 2. That's It! You're Ready

- [ ] Everything else is handled by the single command

### 3. GitHub Configuration (For CI/CD)

- [ ] Repository secrets added: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- [ ] Environments created: `staging`, `production`

## 🚀 Your First Deployment

### Step 1: Start Everything

```bash
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

**That's it!** The interactive menu will guide you through everything:

- 🧪 Test Function Locally
- 🧪 Run Unit Tests
- 🚀 Deploy to STAGING
- 🚀 Deploy to PROD
- And more...

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Initial deployment setup"
git push origin main
```

### Step 3: Monitor GitHub Actions

- Go to: https://github.com/t2modus/Serverless/actions
- Watch the "Lambda Deployment Pipeline" workflow
- Approve staging deployment when prompted

### Step 4: Deploy to Production

- In GitHub Actions, click "Run workflow"
- Select environment: `production`
- Approve the deployment

## 🎯 Your Daily Workflow

1. **Make changes** to Lambda functions
2. **Test locally**: `docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=`
3. **Push to main**: `git push origin main`
4. **Monitor staging**: GitHub Actions deploys to staging
5. **Approve production**: When ready, promote to production

## 🚨 If Something Goes Wrong

### Local Testing Issues

```bash
# Just run the single command - it handles everything
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

### Deployment Issues

```bash
# Just run the single command - it handles everything
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

### GitHub Actions Issues

- Check workflow logs in GitHub
- Verify AWS credentials in repository secrets
- Ensure environments are configured

## 📞 Need Help?

1. **Just run the single command** - it handles everything
2. Check the full setup guide: `SETUP_GUIDE.md`
3. Check GitHub Actions logs for specific errors

---

**🎉 You're all set! Just run this one command for everything:**

```bash
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```
