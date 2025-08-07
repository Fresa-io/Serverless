#!/bin/bash

# Simple Docker deployment script for CDK

echo "🐳 Building Docker container..."
docker build -t app .

if [ $? -eq 0 ]; then
    echo "✅ Container built successfully!"
    echo ""
    echo "🚀 Usage examples:"
    echo ""
    echo "1. Create encrypted credentials hash:"
    echo "   docker run --rm app hash AKIATYDCXTUVLGSA6HMK OinVuEzoBzSxQzDrn9KvYytRpoLjzgObYPaA2KnC us-east-1"
    echo ""
    echo "2. Deploy with encrypted credentials:"
    echo "   docker run --rm app deploy <your_encrypted_hash>"
    echo ""
    echo "3. Show help:"
    echo "   docker run --rm app"
else
    echo "❌ Failed to build container"
    exit 1
fi 