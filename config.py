"""
Configuration file for CDK deployment settings
Update these values with your actual AWS resource names
"""

# Lambda Function Names (replace with your actual deployed function names)
LAMBDA_FUNCTION_NAMES = {
    "recieveEmail": "recieveEmail",                    # Fresa email processing function
    "signUpCustomer": "signUpCustomer",                # Fresa customer signup function
    "verifyCodeAndAuthHandler": "verifyCodeAndAuthHandler",  # Fresa verification function
    "identity_provider_auth": "identity_provider_auth",      # Fresa auth provider function

}

# Lambda Alias Configuration (only STAGING and PROD - DEV is local-only)
LAMBDA_ALIASES = {
    "STAGING": "staging", 
    "PROD": "prod"
}

# Deployment Environment Configuration
DEPLOYMENT_ENV = {
    "STAGING": {
        "alias": "staging",
        "description": "Staging environment for pre-production testing",
        "auto_approve": False  # Requires manual approval
    },
    "PROD": {
        "alias": "prod",
        "description": "Production environment",
        "auto_approve": False  # Requires manual approval
    }
}

# AWS Account and Region Configuration
AWS_CONFIG = {
    "account": None,  # Will use CDK_DEFAULT_ACCOUNT if None
    "region": None,   # Will use CDK_DEFAULT_REGION if None
}

# Stack Configuration
STACK_CONFIG = {
    "stack_name": "FresaLambdaStack",
    "description": "CDK Stack for Fresa Lambda Functions with Alias Management",
}

# GitHub Actions Configuration
GITHUB_CONFIG = {
    "repository": "Fresa/Serverless",  # Your actual repository
    "branch": "main",
    "environments": ["staging", "production"]
}

# Example SQS Queue Configuration (uncomment and update as needed)
# SQS_CONFIG = {
#     "processing_queue_name": "fresa-processing-queue",
#     "visibility_timeout_seconds": 300,
#     "retention_period_days": 14,
# }

# Example S3 Bucket Configuration (uncomment and update as needed)
# S3_CONFIG = {
#     "data_bucket_name": "fresa-data-bucket",
#     "backup_bucket_name": "fresa-backup-bucket",
# }

# Example EventBridge Configuration (uncomment and update as needed)
# EVENTBRIDGE_CONFIG = {
#     "rule_name": "fresa-email-trigger",
#     "schedule_expression": "rate(5 minutes)",  # or "cron(0 12 * * ? *)"
# } 