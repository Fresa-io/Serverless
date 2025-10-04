# 🍓 Fresa SES Template Management Guide

Your original SES template scripts have been successfully integrated into the modular system! Here's how to use them:

## 🎯 **Quick Start**

### **Test Your AWS Credentials**

```bash
python3 services/ses/template_manager.py test-credentials
```

### **Create/Update Templates**

```bash
# Create verification template (your original script)
python3 services/ses/template_manager.py create-verification

# Create welcome template (your original script)
python3 services/ses/template_manager.py create-welcome

# Create both templates at once
python3 services/ses/template_manager.py create-defaults
```

### **Manage Templates**

```bash
# List all templates
python3 services/ses/template_manager.py list

# Get template details
python3 services/ses/template_manager.py get fresa-verificacion-template

# Delete a template
python3 services/ses/remove_template.py fresa-welcome-template
```

## 📧 **Your Original Scripts (Now Integrated)**

### **1. Verification Template (`create_template.py`)**

- **File**: `services/ses/create_verification_template.py`
- **Function**: Creates verification email with Fresa logo
- **Template Name**: `fresa-verificacion-template`
- **Logo URL**: `https://fresaassets.s3.us-east-1.amazonaws.com/fresaicon.png`

### **2. Welcome Template (`create_template_welcome.py`)**

- **File**: `services/ses/create_welcome_template.py`
- **Function**: Creates welcome email with gender-specific greetings
- **Template Name**: `fresa-welcome-template`
- **Features**: Gender-aware greetings, feature list, Fresa branding

### **3. Template Removal (`remove_template.py`)**

- **File**: `services/ses/remove_template.py`
- **Function**: Safely deletes SES templates
- **Usage**: `python3 services/ses/remove_template.py <template_name>`

### **4. AWS Credentials Test (`test_aws_credentials.py`)**

- **File**: `services/ses/test_aws_credentials.py`
- **Function**: Tests AWS credentials and SES access
- **Features**: Lists existing templates, shows account info

## 🚀 **Advanced Usage**

### **Direct Script Usage**

You can still use your original scripts directly:

```bash
# Create verification template directly
python3 services/ses/create_verification_template.py

# Create welcome template directly
python3 services/ses/create_welcome_template.py

# Test AWS credentials directly
python3 services/ses/test_aws_credentials.py

# Remove template directly
python3 services/ses/remove_template.py fresa-welcome-template
```

### **Custom Template Creation**

```bash
# Create custom template
python3 services/ses/template_manager.py create \
  "my-custom-template" \
  "My Subject" \
  "<html>My HTML content</html>" \
  "My text content"

# Update existing template
python3 services/ses/template_manager.py update \
  "fresa-verificacion-template" \
  "Updated Subject" \
  "<html>Updated HTML</html>"
```

## 🎨 **Template Features**

### **Verification Template**

- ✅ Fresa logo integration
- ✅ Professional styling
- ✅ Mobile-responsive design
- ✅ Expiration time display
- ✅ Security messaging

### **Welcome Template**

- ✅ Gender-aware greetings (`{{greeting}} {{name}}`)
- ✅ Feature list with icons
- ✅ Fresa branding
- ✅ Call-to-action
- ✅ Support contact info

## 🔧 **Environment Setup**

Make sure your AWS credentials are set:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

## 📋 **Template Variables**

### **Verification Template Variables**

- `{{verificationCode}}` - The verification code
- `{{expirationMinutes}}` - Expiration time in minutes

### **Welcome Template Variables**

- `{{name}}` - User's name
- `{{greeting}}` - Gender-specific greeting (Bienvenido/Bienvenida)
- `{{excitement_message}}` - Custom excitement message

## 🎯 **Integration Benefits**

✅ **Your original scripts preserved** - All functionality maintained
✅ **Modular system integration** - Works with service orchestrator
✅ **Enhanced error handling** - Better error messages and logging
✅ **AWS info display** - Shows account and region info
✅ **Consistent interface** - Unified command structure
✅ **Backward compatibility** - Original scripts still work

## 🚨 **Troubleshooting**

### **Permission Issues**

If you get permission errors, make sure your AWS user has:

- `ses:CreateTemplate`
- `ses:UpdateTemplate`
- `ses:DeleteTemplate`
- `ses:GetTemplate`
- `ses:ListTemplates`

### **Template Not Found**

If templates don't exist, they'll be created automatically when you run the creation commands.

### **Logo Not Loading**

Make sure the S3 URL is accessible: `https://fresaassets.s3.us-east-1.amazonaws.com/fresaicon.png`

## 🎉 **Success!**

Your SES template scripts are now fully integrated and working! You can use them through the modular system or directly as before.
