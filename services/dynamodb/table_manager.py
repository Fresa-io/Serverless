#!/usr/bin/env python3
"""
DynamoDB Table Manager
Handles creation, configuration, and management of DynamoDB tables
"""

import boto3
import json
import sys
import os
from typing import Dict, List, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from utils.aws_utils import get_aws_account_info, print_aws_info


class DynamoDBTableManager:
    """Manages DynamoDB tables"""

    def __init__(self, region: str = None):
        """Initialize DynamoDB table manager"""
        if region is None:
            region = os.environ.get("AWS_REGION") or "us-east-1"

        self.dynamodb = boto3.client("dynamodb", region_name=region)
        self.region = region

    def create_table(
        self,
        table_name: str,
        key_schema: List[Dict],
        attribute_definitions: List[Dict],
        billing_mode: str = "PAY_PER_REQUEST",
    ) -> bool:
        """Create a DynamoDB table"""
        try:
            table_config = {
                "TableName": table_name,
                "KeySchema": key_schema,
                "AttributeDefinitions": attribute_definitions,
                "BillingMode": billing_mode,
            }

            self.dynamodb.create_table(**table_config)
            print(f"✅ Created DynamoDB table: {table_name}")
            return True

        except Exception as e:
            print(f"❌ Error creating table {table_name}: {e}")
            return False

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        try:
            self.dynamodb.describe_table(TableName=table_name)
            return True
        except:
            return False

    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """Get table information"""
        try:
            response = self.dynamodb.describe_table(TableName=table_name)
            return response.get("Table", {})
        except Exception as e:
            print(f"❌ Error getting table info for {table_name}: {e}")
            return None

    def list_tables(self) -> List[str]:
        """List all tables"""
        try:
            response = self.dynamodb.list_tables()
            return response.get("TableNames", [])
        except Exception as e:
            print(f"❌ Error listing tables: {e}")
            return []

    def delete_table(self, table_name: str) -> bool:
        """Delete a DynamoDB table"""
        try:
            self.dynamodb.delete_table(TableName=table_name)
            print(f"✅ Deleted DynamoDB table: {table_name}")
            return True
        except Exception as e:
            print(f"❌ Error deleting table {table_name}: {e}")
            return False

    def wait_for_table_active(self, table_name: str, timeout: int = 300) -> bool:
        """Wait for table to become active"""
        try:
            waiter = self.dynamodb.get_waiter("table_exists")
            waiter.wait(
                TableName=table_name,
                WaiterConfig={"Delay": 5, "MaxAttempts": timeout // 5},
            )
            print(f"✅ Table {table_name} is now active")
            return True
        except Exception as e:
            print(f"❌ Error waiting for table {table_name}: {e}")
            return False


def create_verification_codes_table() -> bool:
    """Create the VerificationCodes table for email verification"""
    manager = DynamoDBTableManager()

    table_name = "VerificationCodes"

    # Check if table already exists
    if manager.table_exists(table_name):
        print(f"✅ Table {table_name} already exists")
        return True

    # Define table schema
    key_schema = [{"AttributeName": "email", "KeyType": "HASH"}]  # Partition key

    attribute_definitions = [{"AttributeName": "email", "AttributeType": "S"}]  # String

    # Create table
    success = manager.create_table(
        table_name=table_name,
        key_schema=key_schema,
        attribute_definitions=attribute_definitions,
        billing_mode="PAY_PER_REQUEST",
    )

    if success:
        # Wait for table to be active
        manager.wait_for_table_active(table_name)
        print(f"✅ VerificationCodes table created and ready")

    return success


def create_user_sessions_table() -> bool:
    """Create the UserSessions table for user session management"""
    manager = DynamoDBTableManager()

    table_name = "UserSessions"

    # Check if table already exists
    if manager.table_exists(table_name):
        print(f"✅ Table {table_name} already exists")
        return True

    # Define table schema
    key_schema = [{"AttributeName": "session_id", "KeyType": "HASH"}]  # Partition key

    attribute_definitions = [
        {"AttributeName": "session_id", "AttributeType": "S"}  # String
    ]

    # Create table
    success = manager.create_table(
        table_name=table_name,
        key_schema=key_schema,
        attribute_definitions=attribute_definitions,
        billing_mode="PAY_PER_REQUEST",
    )

    if success:
        # Wait for table to be active
        manager.wait_for_table_active(table_name)
        print(f"✅ UserSessions table created and ready")

    return success


def create_all_tables() -> bool:
    """Create all required tables for the application"""
    print("🚀 Creating all DynamoDB tables...")

    success = True

    # Create verification codes table
    if not create_verification_codes_table():
        success = False

    # Create user sessions table
    if not create_user_sessions_table():
        success = False

    if success:
        print("✅ All DynamoDB tables created successfully")
    else:
        print("❌ Some tables failed to create")

    return success


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python services/dynamodb/table_manager.py list")
        print("  python services/dynamodb/table_manager.py create-verification")
        print("  python services/dynamodb/table_manager.py create-sessions")
        print("  python services/dynamodb/table_manager.py create-all")
        print("  python services/dynamodb/table_manager.py info <table_name>")
        print("  python services/dynamodb/table_manager.py delete <table_name>")
        sys.exit(1)

    command = sys.argv[1]
    manager = DynamoDBTableManager()

    # Print AWS info
    print("🔍 DynamoDB Table Manager")
    account_info = print_aws_info()
    if not account_info:
        print("❌ Cannot detect AWS configuration. Please check your credentials.")
        sys.exit(1)
    print()

    if command == "list":
        tables = manager.list_tables()
        print(f"📋 Found {len(tables)} DynamoDB tables:")
        for table in tables:
            print(f"   - {table}")

    elif command == "create-verification":
        create_verification_codes_table()

    elif command == "create-sessions":
        create_user_sessions_table()

    elif command == "create-all":
        create_all_tables()

    elif command == "info":
        if len(sys.argv) < 3:
            print("❌ Table name required")
            sys.exit(1)

        table_name = sys.argv[2]
        info = manager.get_table_info(table_name)
        if info:
            print(f"📄 Table: {table_name}")
            print(f"   Status: {info.get('TableStatus', 'Unknown')}")
            print(f"   Item Count: {info.get('ItemCount', 0)}")
            print(
                f"   Billing Mode: {info.get('BillingModeSummary', {}).get('BillingMode', 'Unknown')}"
            )
            print(f"   Created: {info.get('CreationDateTime', 'Unknown')}")
        else:
            print(f"❌ Table {table_name} not found")

    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Table name required")
            sys.exit(1)

        table_name = sys.argv[2]
        manager.delete_table(table_name)

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
