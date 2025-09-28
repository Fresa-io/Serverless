# 🚀 Fresa AWS Services

This directory contains modular AWS service management scripts for the Fresa application.

## 📁 Structure

```
services/
├── ses/                    # SES (Simple Email Service) management
│   └── template_manager.py # Email template creation/management
├── dynamodb/              # DynamoDB table management
│   └── table_manager.py  # Table creation/management
├── apigateway/           # API Gateway management
│   └── api_manager.py    # API Gateway creation/configuration
└── service_orchestrator.py # Main orchestrator for all services
```

## 🎯 Quick Start

### 1. Set up all services at once:
```bash
python services/service_orchestrator.py setup
```

### 2. Check service status:
```bash
python services/service_orchestrator.py status
```

### 3. Clean up services (use with caution):
```bash
python services/service_orchestrator.py cleanup
```

## 📧 SES Template Management

### Create default email templates:
```bash
python services/ses/template_manager.py create-defaults
```

### List all templates:
```bash
python services/ses/template_manager.py list
```

### Create a custom template:
```bash
python services/ses/template_manager.py create \
  "my-template" \
  "My Subject" \
  "<html>My HTML content</html>" \
  "My text content"
```

### Update a template:
```bash
python services/ses/template_manager.py update \
  "my-template" \
  "Updated Subject" \
  "<html>Updated HTML content</html>"
```

### Delete a template:
```bash
python services/ses/template_manager.py delete my-template
```

## 📊 DynamoDB Table Management

### Create all required tables:
```bash
python services/dynamodb/table_manager.py create-all
```

### Create specific tables:
```bash
# Verification codes table
python services/dynamodb/table_manager.py create-verification

# User sessions table
python services/dynamodb/table_manager.py create-sessions
```

### List all tables:
```bash
python services/dynamodb/table_manager.py list
```

### Get table information:
```bash
python services/dynamodb/table_manager.py info VerificationCodes
```

### Delete a table:
```bash
python services/dynamodb/table_manager.py delete VerificationCodes
```

## 🌐 API Gateway Management

### Create the Fresa API Gateway:
```bash
python services/apigateway/api_manager.py create-fresa
```

### List all APIs:
```bash
python services/apigateway/api_manager.py list
```

### Delete an API:
```bash
python services/apigateway/api_manager.py delete <api_id>
```

## 🔧 Service Configuration

### Required AWS Permissions

Your AWS user/role needs these permissions:

**SES:**
- `ses:CreateTemplate`
- `ses:UpdateTemplate`
- `ses:DeleteTemplate`
- `ses:GetTemplate`
- `ses:ListTemplates`

**DynamoDB:**
- `dynamodb:CreateTable`
- `dynamodb:DescribeTable`
- `dynamodb:ListTables`
- `dynamodb:DeleteTable`

**API Gateway:**
- `apigateway:POST`
- `apigateway:GET`
- `apigateway:DELETE`
- `apigateway:PUT`

**Lambda:**
- `lambda:AddPermission`
- `lambda:GetFunction`

### Environment Variables

Make sure these are set:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

## 📋 Default Services Created

### SES Templates
- `fresa-verificacion-template` - Email verification template

### DynamoDB Tables
- `VerificationCodes` - Stores email verification codes
- `UserSessions` - Stores user session data

### API Gateway
- `Fresa Lambda API` - REST API with STAGING and PRODUCTION endpoints
- STAGING endpoints: `/staging/{function-name}`
- PRODUCTION endpoints: `/prod/{function-name}`

## 🎯 Integration with Lambda Functions

The services are designed to work with your existing Lambda functions:

1. **DynamoDB tables** provide data storage for your Lambda functions
2. **SES templates** are used by your email Lambda functions
3. **API Gateway** exposes your Lambda functions via HTTP endpoints

## 🔄 Workflow

1. **Setup services**: `python services/service_orchestrator.py setup`
2. **Deploy Lambda functions**: Use your existing deployment scripts
3. **Test endpoints**: Use the API Gateway URLs provided
4. **Monitor**: Use `python services/service_orchestrator.py status`

## 🛠️ Customization

### Adding new SES templates:
Edit `services/ses/template_manager.py` and add your templates to the `create_default_templates()` function.

### Adding new DynamoDB tables:
Edit `services/dynamodb/table_manager.py` and add your table schemas.

### Modifying API Gateway:
Edit `services/apigateway/api_manager.py` and update the `create_fresa_api()` function.

## 🚨 Troubleshooting

### Common Issues:

1. **Permission denied**: Check your AWS credentials and permissions
2. **Resource already exists**: Use the individual service managers to check status
3. **API Gateway not working**: Ensure Lambda permissions are set correctly

### Debug Commands:
```bash
# Check AWS configuration
python utils/aws_utils.py

# Check service status
python services/service_orchestrator.py status

# Test individual services
python services/ses/template_manager.py list
python services/dynamodb/table_manager.py list
python services/apigateway/api_manager.py list
```
