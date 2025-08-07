# CDK Transition Phase Deployment Guide

## Step 2: Reference Existing Lambda Functions

This guide helps you transition your existing Lambda functions to CDK management without recreating them.

### Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **CDK CLI installed**: `npm install -g aws-cdk`
3. **Python dependencies installed**: `pip install -r requirements.txt`
4. **Existing Lambda functions deployed** in your AWS account

### Step 1: Find Your Lambda Function Names

First, you need to identify the actual names of your deployed Lambda functions:

```bash
# List all Lambda functions in your account
aws lambda list-functions --query 'Functions[*].FunctionName' --output table

# Or search for specific functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `tracer`)].FunctionName' --output table
```

### Step 2: Update Configuration

Edit `config.py` and replace the placeholder function names with your actual function names:

```python
LAMBDA_FUNCTION_NAMES = {
    "tracer_import_results": "your-actual-tracer-import-results-function-name",
    "tracer_sqs_consumer": "your-actual-tracer-sqs-consumer-function-name",
}
```

### Step 3: Deploy the CDK Stack

```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Synthesize the CloudFormation template
cdk synth

# Deploy the stack
cdk deploy
```

### Step 4: Verify the Deployment

After deployment, you should see outputs like:

```
Outputs:
TracerLambdaStack.TracerImportResultsArn = arn:aws:lambda:region:account:function:your-function-name
TracerLambdaStack.TracerSqsConsumerArn = arn:aws:lambda:region:account:function:your-function-name
```

### What This Accomplishes

✅ **References existing functions** without recreating them  
✅ **Adds CloudWatch Logs permissions** to both functions  
✅ **Provides a foundation** for adding more permissions and triggers  
✅ **Outputs function ARNs** for reference

### Next Steps

Once this is working, you can uncomment and customize the example configurations:

1. **SQS Integration**: Uncomment the SQS queue creation and permissions
2. **S3 Integration**: Uncomment the S3 bucket permissions
3. **EventBridge Rules**: Uncomment the scheduled triggers
4. **Additional Permissions**: Add more IAM policies as needed

### Troubleshooting

**Error: Function not found**

- Verify the function names in `config.py` match your actual deployed functions
- Check that you're in the correct AWS account/region

**Error: Permission denied**

- Ensure your AWS credentials have Lambda and IAM permissions
- Check that CDK is bootstrapped in your account

**Error: Import config failed**

- Make sure you're running from the correct directory
- Verify the `config.py` file exists in the CDK root directory

### Safety Notes

⚠️ **This is a transition phase** - your existing functions remain unchanged  
⚠️ **Only permissions are added** - no function code or configuration is modified  
⚠️ **Easy to rollback** - you can delete the CDK stack without affecting your functions

### Useful Commands

```bash
# Check stack status
cdk diff

# Destroy stack (if needed)
cdk destroy

# List all stacks
cdk list

# View stack outputs
aws cloudformation describe-stacks --stack-name TracerLambdaStack --query 'Stacks[0].Outputs'
```
