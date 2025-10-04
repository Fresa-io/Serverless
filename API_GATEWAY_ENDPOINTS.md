# 🌐 API Gateway Endpoints Guide

## 🎯 **Your Current API Gateway Setup**

### **Base URLs:**

- **PRODUCTION**: `https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/prod`
- **STAGING**: `https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/staging`

### **Available Endpoints:**

#### **📧 Email Processing:**

- **STAGING**: `POST https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/staging/recieve-email`
- **PRODUCTION**: `POST https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/prod/recieve-email`

#### **👤 Customer Signup:**

- **STAGING**: `POST https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/staging/signup-customer`
- **PRODUCTION**: `POST https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/prod/signup-customer`

## 🔄 **What Your Callers Need to Update**

### **1. Frontend Applications**

Update your frontend API calls to use the appropriate environment:

```javascript
// Environment-based configuration
const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? "https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/prod"
    : "https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/staging";

// Email processing
const emailEndpoint = `${API_BASE_URL}/recieve-email`;

// Customer signup
const signupEndpoint = `${API_BASE_URL}/signup-customer`;
```

### **2. Mobile Applications**

Update your mobile app API calls:

```swift
// iOS Swift
let baseURL = Bundle.main.object(forInfoDictionaryKey: "API_BASE_URL") as? String ?? ""
let emailEndpoint = "\(baseURL)/recieve-email"
let signupEndpoint = "\(baseURL)/signup-customer"
```

```kotlin
// Android Kotlin
val baseURL = BuildConfig.API_BASE_URL
val emailEndpoint = "$baseURL/recieve-email"
val signupEndpoint = "$baseURL/signup-customer"
```

### **3. Server-to-Server Calls**

Update your backend services:

```python
# Python
import os

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/staging')
EMAIL_ENDPOINT = f"{API_BASE_URL}/recieve-email"
SIGNUP_ENDPOINT = f"{API_BASE_URL}/signup-customer"
```

```javascript
// Node.js
const API_BASE_URL =
  process.env.API_BASE_URL ||
  "https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/staging";
const emailEndpoint = `${API_BASE_URL}/recieve-email`;
const signupEndpoint = `${API_BASE_URL}/signup-customer`;
```

## 🎯 **Environment Configuration**

### **Development/Testing:**

```bash
API_BASE_URL=https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/staging
```

### **Production:**

```bash
API_BASE_URL=https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/prod
```

## 📋 **Lambda Function Aliases**

Your Lambda functions are configured with aliases:

### **STAGING Aliases:**

- `recieveEmail:staging` → Latest staging version
- `signUpCustomer:staging` → Latest staging version

### **PRODUCTION Aliases:**

- `recieveEmail:prod` → Latest production version
- `signUpCustomer:prod` → Latest production version

## 🔧 **Testing Your Endpoints**

### **Test STAGING Endpoints:**

```bash
# Test email processing (STAGING)
curl -X POST https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/staging/recieve-email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "message": "Test message"}'

# Test customer signup (STAGING)
curl -X POST https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/staging/signup-customer \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User"}'
```

### **Test PRODUCTION Endpoints:**

```bash
# Test email processing (PRODUCTION)
curl -X POST https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/prod/recieve-email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "message": "Test message"}'

# Test customer signup (PRODUCTION)
curl -X POST https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com/prod/signup-customer \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User"}'
```

## 🚀 **Deployment Strategy**

### **1. Update Development/Testing:**

- Point to STAGING endpoints
- Test with staging data
- Verify functionality

### **2. Update Production:**

- Point to PRODUCTION endpoints
- Use production data
- Monitor performance

### **3. Gradual Rollout:**

- Start with a small percentage of traffic
- Monitor for errors
- Gradually increase traffic

## 📊 **Monitoring & Analytics**

### **CloudWatch Metrics:**

- API Gateway request count
- Lambda function duration
- Error rates
- Throttling

### **Logs:**

- API Gateway access logs
- Lambda function logs
- Error tracking

## 🎯 **Next Steps**

1. **Update your frontend/mobile apps** to use the new endpoints
2. **Test both STAGING and PRODUCTION** endpoints
3. **Update your environment variables** in your deployment pipeline
4. **Monitor the endpoints** for performance and errors
5. **Gradually migrate traffic** from old endpoints to new ones

## 🔗 **Quick Reference**

| Service          | STAGING Endpoint           | PRODUCTION Endpoint     |
| ---------------- | -------------------------- | ----------------------- |
| Email Processing | `/staging/recieve-email`   | `/prod/recieve-email`   |
| Customer Signup  | `/staging/signup-customer` | `/prod/signup-customer` |

**Base URL**: `https://5cxyrbm6pk.execute-api.us-east-1.amazonaws.com`
