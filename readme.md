# Source Control for Cloud Infrastructure ☁️

This repository provides source control for our AWS cloud infrastructure (serverless code)

---

## 🚀 Quick Start (For Developers)

### Prerequisites

- Docker installed on your system (Windows, macOS, or Linux)
- **Ask your admin for the encrypted credentials hash**

### One-Command Deployment

```bash
docker run --rm app deploy <encrypted_credentials_hash>
```

**Example:**

```bash
docker run --rm app deploy QUtJQVRZRENYVFVWTEZTQTZITUs6T2luVnVFem9CelpTeFF6RHJuOUt2WXl0UnBvTGp6Z09iWVBhQTJLbkM6dXMtZWFzdC0x
```

### 🔑 Getting the Encrypted Credentials Hash

**Ask your admin/team lead for the encrypted credentials hash.** They will provide you with a long string that looks like this:

```
QUtJQVRZRENYVFVWTEZTQTZITUs6T2luVnVFem9CelpTeFF6RHJuOUt2WXl0UnBvTGp6Z09iWVBhQTJLbkM6dXMtZWFzdC0x
```

**You do NOT need to create this yourself** - only admins should generate encrypted credentials.

---

## 🔐 Security Features

- **Credential Encryption**: Credentials are base64 encoded for safe sharing
- **No Local Storage**: Credentials are never stored on disk
- **Container Isolation**: All operations happen in isolated Docker container
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🛠️ What the Container Does

1. **Sets up AWS CLI** with your credentials
2. **Installs Python dependencies** (CDK, etc.)
3. **Configures CDK** environment
4. **Bootstraps CDK** (if needed)
5. **Deploys your stack** with proper permissions
6. **Outputs results** and stack information

## 📁 File Structure

```
Serverless/
├── Dockerfile              # Container definition
├── entrypoint.sh           # Main deployment script
├── encrypt_utils.py        # Credential encryption utility
├── generate-hash.sh        # Helper script for credential generation (ADMIN ONLY)
├── config.py              # CDK configuration
├── app.py                 # CDK app entry point
├── cdk/
│   └── cdk_stack.py       # Main CDK stack
├── requirements.txt       # Python dependencies
├── cdk.json              # CDK configuration
└── Lambdas/              # Your Lambda function code
    └── Expansion/
        ├── tracer_import_results/
        └── tracer_sqs_consumer/
```

## 🔧 Customization

### Update Lambda Function Names

Edit `config.py` to match your actual deployed Lambda function names:

```python
LAMBDA_FUNCTION_NAMES = {
    "tracer_import_results": "your-actual-function-name",
    "tracer_sqs_consumer": "your-actual-function-name",
}
```

### Add More AWS Resources

Uncomment and customize the examples in `cdk/cdk_stack.py`:

- SQS queues
- S3 buckets
- EventBridge rules
- Additional IAM permissions

## 🚨 Troubleshooting

### Common Issues

**Error: "Function not found"**

- Verify function names in `config.py` match your actual deployed functions
- Check that you're in the correct AWS account/region

**Error: "AWS connection failed"**

- Verify your AWS credentials are correct
- Ensure your AWS account has the necessary permissions

**Error: "CDK bootstrap failed"**

- This is normal if CDK is already bootstrapped
- The deployment will continue

**Error: "Permission denied"**

- Ensure your AWS credentials have Lambda and IAM permissions
- Check that CDK is bootstrapped in your account

**Error: "Failed to decrypt credentials"**

- Make sure you're using the exact hash provided by your admin
- Check that the hash hasn't been modified or truncated
- Ask your admin to generate a new hash if needed

### Debug Commands

```bash
# Test AWS connection
docker run --rm app aws sts get-caller-identity

# List Lambda functions
docker run --rm app aws lambda list-functions

# Check CDK status
docker run --rm app cdk diff
```

## 📊 Deployment Output

Successful deployment will show:

```
✅ AWS connection successful
👤 Identity: arn:aws:iam::123456789012:user/your-user
📋 Checking existing Lambda functions...
🚀 Bootstrapping CDK...
🚀 Deploying CDK stack...
✅ Deployment completed successfully!

📊 Stack outputs:
TracerLambdaStack
```

## 🎯 Benefits

- **Single Command**: Complete deployment with one Docker command
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Secure**: Credentials are encrypted and never stored
- **Team-Friendly**: Share encrypted hashes instead of raw credentials
- **No Setup**: No need to install AWS CLI, Python, or CDK locally
- **Isolated**: All dependencies contained in Docker container

## 🔄 Workflow for Teams

1. **Admin** creates encrypted hash and shares with team
2. **Developers** use hash to deploy without seeing raw credentials
3. **All developers** can deploy using the same secure hash
4. **No credentials** are stored in version control

---

## 🔑 For Admins: How to Generate Encrypted Credentials

**This section is for admins only. Developers should ask you for the hash.**

If you need to create new encrypted credentials or your current ones have expired, follow these steps:

### Option 1: Easy Way (Recommended)

Use the helper script for interactive credential input:

```bash
./generate-hash.sh
```

This will prompt you for your credentials and generate the exact command to use.

### Option 2: Manual Way

#### Step 1: Create Encrypted Credentials Hash

```bash
docker run --rm app hash <your_access_key> <your_secret_key> <your_region>
```

**Example:**

```bash
docker run --rm app hash AKIATYDCXTUVLGSA6HMK OinVuEzoBzSxQzDrn9KvYytRpoLjzgObYPaA2KnC us-east-1
```

**Output:**

```
🔐 Creating encrypted credentials hash...
✅ Encrypted credentials hash:
QUtJQVRZRENYVFVWTEZTQTZITUs6T2luVnVFem9CelpTeFF6RHJuOUt2WXl0UnBvTGp6Z09iWVBhQTJLbkM6dXMtZWFzdC0x

📋 Use this hash for deployment:
docker run --rm app deploy QUtJQVRZRENYVFVWTEZTQTZITUs6T2luVnVFem9CelpTeFF6RHJuOUt2WXl0UnBvTGp6Z09iWVBhQTJLbkM6dXMtZWFzdC0x
```

#### Step 2: Share with Your Team

Copy the generated hash and share it with your developers. They will use it like this:

```bash
docker run --rm app deploy <your_generated_hash>
```

### Getting AWS Credentials

1. **Go to AWS Console** → IAM → Users → Your User
2. **Security credentials tab** → Create access key
3. **Choose use case**: Application running outside AWS
4. **Download the CSV file** with your credentials

---

### Key Features

- **Version Control:** We can track and review every change made to our cloud infrastructure, with a special focus on our Lambda functions.
- **Safe Rollbacks:** The version history allows us to safely roll back to a previous state if needed.
- **Collaborative Development:** Using pull requests and code reviews, we can collaborate more effectively on our infrastructure code.
- **Docker Deployment:** Single-command deployment using Docker with encrypted credentials.

---

### Future Improvements (Nice to Have – Not Required as of 07-30-25)

- Improve deployment by integrating with **CI/CD pipelines**.
- Keep **infrastructure-as-code (IaC)** in a single, organized location to improve maintenance and scalability.
