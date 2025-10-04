#!/usr/bin/env python3
"""
Service Orchestrator
Manages all AWS services for the Fresa application
"""

import sys
import os
from pathlib import Path
from typing import Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.aws_utils import get_aws_account_info, print_aws_info
from services.ses.template_manager import SESTemplateManager, create_default_templates
from services.dynamodb.table_manager import DynamoDBTableManager, create_all_tables
from services.apigateway.api_manager import APIGatewayManager, create_fresa_api


class ServiceOrchestrator:
    """Orchestrates all AWS services for the Fresa application"""

    def __init__(self):
        """Initialize the service orchestrator"""
        self.ses_manager = SESTemplateManager()
        self.dynamodb_manager = DynamoDBTableManager()
        self.apigateway_manager = APIGatewayManager()

    def setup_all_services(self) -> bool:
        """Set up all required AWS services"""
        print("🚀 Setting up all AWS services for Fresa application...")
        print("=" * 60)

        success = True

        # 1. Create DynamoDB tables
        print("\n📊 Step 1: Creating DynamoDB tables...")
        if not create_all_tables():
            print("❌ Failed to create DynamoDB tables")
            success = False
        else:
            print("✅ DynamoDB tables created successfully")

        # 2. Create SES templates
        print("\n📧 Step 2: Creating SES email templates...")
        if not create_default_templates():
            print("❌ Failed to create SES templates")
            success = False
        else:
            print("✅ SES templates created successfully")

        # 3. Create API Gateway
        print("\n🌐 Step 3: Creating API Gateway...")
        api_id = create_fresa_api()
        if not api_id:
            print("❌ Failed to create API Gateway")
            success = False
        else:
            print("✅ API Gateway created successfully")

        # Summary
        print("\n" + "=" * 60)
        if success:
            print("🎉 All AWS services set up successfully!")
            print("\n📋 Next steps:")
            print("1. Update your Lambda function environment variables if needed")
            print("2. Test your API endpoints")
            print("3. Deploy your Lambda functions with the new aliases")
        else:
            print("❌ Some services failed to set up. Check the errors above.")

        return success

    def check_service_status(self) -> Dict:
        """Check the status of all services"""
        print("🔍 Checking AWS service status...")
        print("=" * 60)

        status = {
            "dynamodb": {"tables": [], "status": "unknown"},
            "ses": {"templates": [], "status": "unknown"},
            "apigateway": {"apis": [], "status": "unknown"},
            "lambda": {"functions": [], "status": "unknown"},
        }

        # Check DynamoDB
        try:
            tables = self.dynamodb_manager.list_tables()
            status["dynamodb"]["tables"] = tables
            status["dynamodb"]["status"] = "available"
            print(f"✅ DynamoDB: {len(tables)} tables found")
        except Exception as e:
            status["dynamodb"]["status"] = "error"
            print(f"❌ DynamoDB: {e}")

        # Check SES
        try:
            templates = self.ses_manager.list_templates()
            status["ses"]["templates"] = [t["Name"] for t in templates]
            status["ses"]["status"] = "available"
            print(f"✅ SES: {len(templates)} templates found")
        except Exception as e:
            status["ses"]["status"] = "error"
            print(f"❌ SES: {e}")

        # Check API Gateway
        try:
            apis = self.apigateway_manager.list_apis()
            status["apigateway"]["apis"] = [
                {"name": api["name"], "id": api["id"]} for api in apis
            ]
            status["apigateway"]["status"] = "available"
            print(f"✅ API Gateway: {len(apis)} APIs found")
        except Exception as e:
            status["apigateway"]["status"] = "error"
            print(f"❌ API Gateway: {e}")

        return status

    def cleanup_services(self) -> bool:
        """Clean up all services (use with caution!)"""
        print("⚠️  WARNING: This will delete all AWS resources!")
        print("This action cannot be undone.")

        confirm = input("Type 'DELETE' to confirm: ")
        if confirm != "DELETE":
            print("❌ Cleanup cancelled")
            return False

        print("🧹 Cleaning up AWS services...")

        # Delete API Gateway APIs
        try:
            apis = self.apigateway_manager.list_apis()
            for api in apis:
                if "Fresa" in api["name"]:
                    self.apigateway_manager.delete_api(api["id"])
        except Exception as e:
            print(f"❌ Error cleaning up API Gateway: {e}")

        # Delete DynamoDB tables
        try:
            tables = self.dynamodb_manager.list_tables()
            for table in ["VerificationCodes", "UserSessions"]:
                if table in tables:
                    self.dynamodb_manager.delete_table(table)
        except Exception as e:
            print(f"❌ Error cleaning up DynamoDB: {e}")

        print("✅ Cleanup completed")
        return True


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python services/service_orchestrator.py setup")
        print("  python services/service_orchestrator.py status")
        print("  python services/service_orchestrator.py cleanup")
        sys.exit(1)

    command = sys.argv[1]
    orchestrator = ServiceOrchestrator()

    # Print AWS info
    print("🔍 Fresa Service Orchestrator")
    account_info = print_aws_info()
    if not account_info:
        print("❌ Cannot detect AWS configuration. Please check your credentials.")
        sys.exit(1)
    print()

    if command == "setup":
        orchestrator.setup_all_services()

    elif command == "status":
        orchestrator.check_service_status()

    elif command == "cleanup":
        orchestrator.cleanup_services()

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
