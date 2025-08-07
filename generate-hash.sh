#!/bin/bash

# Helper script to generate encrypted credentials hash

echo "🔐 AWS Credentials Hash Generator"
echo "=================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if app image exists, if not build it
if ! docker image inspect app &> /dev/null; then
    echo "🐳 Building Docker container..."
    docker build -t app .
    if [ $? -ne 0 ]; then
        echo "❌ Failed to build Docker container"
        exit 1
    fi
    echo "✅ Container built successfully!"
fi

echo ""
echo "📝 Enter your AWS credentials:"
echo ""

read -p "AWS Access Key ID: " ACCESS_KEY
read -s -p "AWS Secret Access Key: " SECRET_KEY
echo ""
read -p "AWS Region (e.g., us-east-1): " REGION

echo ""
echo "🔐 Generating encrypted hash..."

# Generate the hash
HASH_OUTPUT=$(docker run --rm app hash "$ACCESS_KEY" "$SECRET_KEY" "$REGION")

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Hash generated successfully!"
    echo ""
    echo "📋 Copy this exact command for deployment:"
    echo ""
    echo "$HASH_OUTPUT" | grep "docker run --rm app deploy"
    echo ""
    echo "🔒 Your credentials are now encrypted and safe to share!"
else
    echo "❌ Failed to generate hash"
    exit 1
fi 