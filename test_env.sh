#!/bin/bash

# Test environment variables for local testing
export DYNAMODB_TABLE_NAME="test-verification-codes"
export COGNITO_CLIENT_ID="test-client-id"
export COGNITO_USER_POOL_ID="test-user-pool-id"
export CODE_EXPIRATION_MINUTES="5"
export AWS_REGION="us-east-1"
export SES_FROM_EMAIL_ADDRESS="test@example.com"
export SES_VERIFICATION_TEMPLATE_NAME="test-template"
export SENDER_EMAIL="admin@fresa.live"

echo "✅ Environment variables set for testing"
echo "DYNAMODB_TABLE_NAME: $DYNAMODB_TABLE_NAME"
echo "COGNITO_CLIENT_ID: $COGNITO_CLIENT_ID"
echo "COGNITO_USER_POOL_ID: $COGNITO_USER_POOL_ID"
