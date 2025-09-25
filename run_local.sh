#!/bin/bash

# 🚀 Local Development Runner
# This script loads your local credentials and runs the CLI

# Load local credentials
source ./local_credentials.sh

# Run the updated CLI with your actual credentials
./run_updated_cli.sh "$LOCAL_AWS_CREDENTIALS"
