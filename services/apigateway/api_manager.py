#!/usr/bin/env python3
"""
API Gateway Manager
Handles creation, configuration, and management of API Gateway resources
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
from config import LAMBDA_FUNCTION_NAMES


class APIGatewayManager:
    """Manages API Gateway resources"""

    def __init__(self, region: str = None):
        """Initialize API Gateway manager"""
        if region is None:
            region = os.environ.get("AWS_REGION") or "us-east-1"

        self.apigateway = boto3.client("apigateway", region_name=region)
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.region = region
        self.account_id = get_aws_account_info()["account_id"]

    def create_rest_api(self, name: str, description: str = None) -> Optional[str]:
        """Create a new REST API"""
        try:
            response = self.apigateway.create_rest_api(
                name=name,
                description=description or f"API Gateway for {name}",
                endpointConfiguration={"types": ["REGIONAL"]},
            )

            api_id = response["id"]
            print(f"✅ Created REST API: {api_id}")
            print(f"   Name: {response['name']}")
            print(f"   Description: {response['description']}")

            return api_id

        except Exception as e:
            print(f"❌ Error creating REST API: {e}")
            return None

    def get_api_resources(self, api_id: str) -> Dict[str, str]:
        """Get all resources for an API"""
        try:
            response = self.apigateway.get_resources(restApiId=api_id)
            resource_map = {}

            for resource in response["items"]:
                path = resource["path"]
                resource_id = resource["id"]
                resource_map[path] = resource_id

            return resource_map

        except Exception as e:
            print(f"❌ Error getting API resources: {e}")
            return {}

    def create_resource(
        self, api_id: str, parent_id: str, path_part: str
    ) -> Optional[str]:
        """Create a new resource"""
        try:
            response = self.apigateway.create_resource(
                restApiId=api_id, parentId=parent_id, pathPart=path_part
            )

            resource_id = response["id"]
            print(f"✅ Created resource: {path_part} (ID: {resource_id})")
            return resource_id

        except Exception as e:
            print(f"❌ Error creating resource {path_part}: {e}")
            return None

    def add_method(
        self,
        api_id: str,
        resource_id: str,
        http_method: str,
        authorization_type: str = "NONE",
    ) -> bool:
        """Add HTTP method to resource"""
        try:
            self.apigateway.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                authorizationType=authorization_type,
            )

            print(f"✅ Added {http_method} method to resource")
            return True

        except Exception as e:
            print(f"❌ Error adding {http_method} method: {e}")
            return False

    def add_lambda_integration(
        self,
        api_id: str,
        resource_id: str,
        http_method: str,
        function_name: str,
        alias: str = None,
    ) -> bool:
        """Add Lambda integration to method"""
        try:
            # Construct Lambda function ARN
            if alias:
                function_arn = f"arn:aws:lambda:{self.region}:{self.account_id}:function:{function_name}:{alias}"
            else:
                function_arn = f"arn:aws:lambda:{self.region}:{self.account_id}:function:{function_name}"

            integration_uri = f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{function_arn}/invocations"

            self.apigateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                type="AWS_PROXY",
                integrationHttpMethod="POST",
                uri=integration_uri,
            )

            print(f"✅ Added Lambda integration: {function_name}:{alias or 'LATEST'}")
            return True

        except Exception as e:
            print(f"❌ Error adding Lambda integration: {e}")
            return False

    def add_lambda_permission(
        self, function_name: str, alias: str, api_id: str
    ) -> bool:
        """Add permission for API Gateway to invoke Lambda function"""
        try:
            statement_id = f"api-gateway-{function_name}-{alias or 'latest'}"
            source_arn = (
                f"arn:aws:execute-api:{self.region}:{self.account_id}:{api_id}/*/*"
            )

            if alias:
                function_qualified_name = f"{function_name}:{alias}"
            else:
                function_qualified_name = function_name

            self.lambda_client.add_permission(
                FunctionName=function_qualified_name,
                StatementId=statement_id,
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=source_arn,
            )

            print(f"✅ Added Lambda permission: {function_qualified_name}")
            return True

        except Exception as e:
            if "already exists" in str(e):
                print(
                    f"✅ Permission already exists for {function_name}:{alias or 'LATEST'}"
                )
                return True
            else:
                print(f"❌ Error adding Lambda permission: {e}")
                return False

    def deploy_api(
        self, api_id: str, stage_name: str = "prod", description: str = None
    ) -> bool:
        """Deploy API to stage"""
        try:
            self.apigateway.create_deployment(
                restApiId=api_id,
                stageName=stage_name,
                description=description or f"Deployment to {stage_name} stage",
            )

            print(f"✅ Deployed API to stage: {stage_name}")
            return True

        except Exception as e:
            print(f"❌ Error deploying API: {e}")
            return False

    def create_lambda_api(
        self, api_name: str, functions_config: List[Dict]
    ) -> Optional[str]:
        """Create a complete API Gateway with Lambda integrations"""
        try:
            # Create REST API
            api_id = self.create_rest_api(api_name)
            if not api_id:
                return None

            # Get root resource
            resources = self.get_api_resources(api_id)
            root_id = resources.get("/", None)
            if not root_id:
                print("❌ Could not find root resource")
                return None

            # Create environment resources (staging, prod)
            staging_id = self.create_resource(api_id, root_id, "staging")
            prod_id = self.create_resource(api_id, root_id, "prod")

            if not staging_id or not prod_id:
                print("❌ Could not create environment resources")
                return None

            # Create function resources and integrations
            for func_config in functions_config:
                function_name = func_config["function_name"]
                endpoint_name = func_config.get("endpoint_name", function_name)

                # Create staging endpoint
                staging_func_id = self.create_resource(
                    api_id, staging_id, endpoint_name
                )
                if staging_func_id:
                    self.add_method(api_id, staging_func_id, "POST")
                    self.add_lambda_integration(
                        api_id, staging_func_id, "POST", function_name, "staging"
                    )
                    self.add_lambda_permission(function_name, "staging", api_id)

                # Create production endpoint
                prod_func_id = self.create_resource(api_id, prod_id, endpoint_name)
                if prod_func_id:
                    self.add_method(api_id, prod_func_id, "POST")
                    self.add_lambda_integration(
                        api_id, prod_func_id, "POST", function_name, "prod"
                    )
                    self.add_lambda_permission(function_name, "prod", api_id)

            # Deploy API
            self.deploy_api(api_id)

            # Print endpoints
            base_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/prod"
            print(f"\n🎉 API Gateway created successfully!")
            print(f"   API ID: {api_id}")
            print(f"   Base URL: {base_url}")
            print(f"   STAGING endpoints:")
            for func_config in functions_config:
                endpoint_name = func_config.get(
                    "endpoint_name", func_config["function_name"]
                )
                print(f"     - {base_url}/staging/{endpoint_name}")
            print(f"   PRODUCTION endpoints:")
            for func_config in functions_config:
                endpoint_name = func_config.get(
                    "endpoint_name", func_config["function_name"]
                )
                print(f"     - {base_url}/prod/{endpoint_name}")

            return api_id

        except Exception as e:
            print(f"❌ Error creating Lambda API: {e}")
            return None

    def list_apis(self) -> List[Dict]:
        """List all REST APIs"""
        try:
            response = self.apigateway.get_rest_apis()
            return response.get("items", [])
        except Exception as e:
            print(f"❌ Error listing APIs: {e}")
            return []

    def delete_api(self, api_id: str) -> bool:
        """Delete a REST API"""
        try:
            self.apigateway.delete_rest_api(restApiId=api_id)
            print(f"✅ Deleted API: {api_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting API: {e}")
            return False


def create_fresa_api() -> Optional[str]:
    """Create the Fresa API Gateway with all Lambda functions"""
    manager = APIGatewayManager()

    # Define function configurations
    functions_config = [
        {"function_name": "recieveEmail", "endpoint_name": "recieve-email"},
        {"function_name": "signUpCustomer", "endpoint_name": "signup-customer"},
        {"function_name": "verifyCodeAndAuthHandler", "endpoint_name": "verify-code"},
        {"function_name": "identity_provider_auth", "endpoint_name": "identity-auth"},
        {"function_name": "social_auth_user", "endpoint_name": "social-auth"},
        {"function_name": "defineAuthChallenge", "endpoint_name": "define-challenge"},
        {"function_name": "verifyAuthChallenge", "endpoint_name": "verify-challenge"},
        {"function_name": "createAuthChallenge", "endpoint_name": "create-challenge"},
    ]

    return manager.create_lambda_api("Fresa Lambda API", functions_config)


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python services/apigateway/api_manager.py list")
        print("  python services/apigateway/api_manager.py create-fresa")
        print("  python services/apigateway/api_manager.py delete <api_id>")
        sys.exit(1)

    command = sys.argv[1]
    manager = APIGatewayManager()

    # Print AWS info
    print("🔍 API Gateway Manager")
    account_info = print_aws_info()
    if not account_info:
        print("❌ Cannot detect AWS configuration. Please check your credentials.")
        sys.exit(1)
    print()

    if command == "list":
        apis = manager.list_apis()
        print(f"📋 Found {len(apis)} REST APIs:")
        for api in apis:
            print(f"   - {api['name']} (ID: {api['id']})")
            print(f"     Created: {api['createdDate']}")
            print(f"     Description: {api.get('description', 'No description')}")

    elif command == "create-fresa":
        create_fresa_api()

    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ API ID required")
            sys.exit(1)

        api_id = sys.argv[2]
        manager.delete_api(api_id)

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
