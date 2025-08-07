# Enhanced Lambda Deployment System

A comprehensive Lambda deployment system with alias management, local testing, and interactive deployment workflows.

## 🚀 Quick Start

### 1. Build the Container

```bash
docker build -t app .
```

### 2. Setup Credentials (First Time Only)

```bash
# Generate encrypted credentials hash
docker run --rm app hash AKIATYDCXTUVLGSA6HMK OinVuEzoBzSxQzDrn9KvYytRpoLjzgObYPaA2KnC us-east-1
```

### 3. Start Deployment (That's It!)

```bash
# Start the interactive deployment system
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```

This opens an interactive menu where you can:

- Test functions locally
- Run unit tests
- Deploy to STAGING/PROD
- Check deployment status
- And much more!

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

## 🎮 Interactive Menu

The interactive menu provides easy access to all deployment operations:

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

### 🔄 Re-initiating the Menu

**From Interactive Shell:**

- Type `menu` to return to the interactive menu
- Type `exit` to leave the shell and return to menu

**From Command Line:**

- Just run the same command again: `docker run --rm -it app deploy <credentials>`

### 🛡️ Safety Features

- **✅ Functions Never Deleted**: Only updated with new versions
- **✅ Aliases Never Deleted**: Only updated to point to new versions
- **✅ Version History Preserved**: All versions are kept
- **✅ Rollback Capability**: Easy rollback to previous versions
- **✅ Function Existence Check**: Verifies functions exist before operations
- **✅ Safe Updates**: Only updates, never deletes resources

## 🎯 Best Practices

1. **Use the Single Command** - `docker run --rm -it app deploy <credentials>`
2. **Test Locally First** - Always test before deploying
3. **Validate in STAGING** - Test in STAGING before PROD
4. **Monitor Deployments** - Check status after each deployment
5. **Keep Version History** - Don't delete old versions

---

## 🎉 Summary

This enhanced Lambda deployment system provides:

- **🎮 Single Command**: Just one command to start everything
- **🔒 Safe**: No accidental production changes
- **🔄 Flexible**: Easy environment promotion
- **🧪 Testable**: Local testing without affecting production
- **📋 Automated**: GitHub Actions CI/CD pipeline
- **🛡️ Reliable**: Version history and rollback capability

**Usage**: Just run this one command!

```bash
docker run --rm -it app deploy QUtJQVRZRENYVFVWTEdTQTZITUs6T2luVnVFem9CelN4UXpEcm45S3ZZeXRScG9ManpnT2JZUGFBMktuQzp1cy1lYXN0LTE=
```
