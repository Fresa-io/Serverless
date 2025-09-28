#!/usr/bin/env python3
"""
Enhanced Lambda Deployment Script with Alias Management
Deploys Lambda functions with proper alias management for STAGING and PROD environments
DEV environment is local-only, no deployment needed
"""

import boto3
import json
import sys
import os
import zipfile
import tempfile
import shutil
from typing import Dict, List, Optional
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LAMBDA_FUNCTION_NAMES, LAMBDA_ALIASES, DEPLOYMENT_ENV
from scripts.lambda_alias_manager import LambdaAliasManager
from utils.aws_utils import get_aws_account_info, get_lambda_execution_role_arn


class LambdaDeployer:
    def __init__(self, region: str = None):
        """Initialize the Lambda deployer"""
        # Use environment variable or default region if none provided
        if region is None:
            region = (
                os.environ.get("AWS_REGION")
                or os.environ.get("CDK_DEFAULT_REGION")
                or "us-east-1"
            )
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.s3_client = boto3.client("s3", region_name=region)
        self.functions = LAMBDA_FUNCTION_NAMES
        self.aliases = LAMBDA_ALIASES
        self.environments = DEPLOYMENT_ENV
        self.alias_manager = LambdaAliasManager(region)

    def create_deployment_package(
        self, function_path: str, output_path: str = None
    ) -> str:
        """Create a deployment package (ZIP file) for a Lambda function"""
        if not output_path:
            output_path = f"{function_path}.zip"

        print(f"📦 Creating deployment package: {output_path}")

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Add all files in the function directory
            for root, dirs, files in os.walk(function_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, function_path)

                    # Skip __pycache__ and .pyc files
                    if "__pycache__" in file_path or file.endswith(".pyc"):
                        continue

                    zipf.write(file_path, arc_name)
                    print(f"  📄 Added: {arc_name}")

        print(f"✅ Deployment package created: {output_path}")
        return output_path

    def create_lambda_function(
        self, function_name: str, zip_path: str, handler: str = None
    ) -> bool:
        """Create a new Lambda function"""
        try:
            print(f"🆕 Creating new Lambda function: {function_name}...")

            # Default handler if not provided
            if not handler:
                handler = f"{function_name}.lambda_handler"

            # Get AWS account ID for role ARN (dynamic detection)
            role_arn = get_lambda_execution_role_arn()

            # Create the function
            with open(zip_path, "rb") as zip_file:
                response = self.lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime="python3.9",
                    Role=role_arn,
                    Handler=handler,
                    Code={"ZipFile": zip_file.read()},
                    Description=f"Lambda function for {function_name}",
                    Timeout=30,
                    MemorySize=128,
                )

            print(f"✅ Successfully created Lambda function: {function_name}")
            return True

        except Exception as e:
            print(f"❌ Error creating Lambda function {function_name}: {e}")
            return False

    def update_function_code(self, function_name: str, zip_path: str) -> bool:
        """Update Lambda function code"""
        try:
            print(f"🔄 Updating function code for {function_name}...")

            # Safety check: Verify function exists before updating
            try:
                self.lambda_client.get_function(FunctionName=function_name)
            except self.lambda_client.exceptions.ResourceNotFoundException:
                print(f"❌ Function {function_name} does not exist. Cannot update.")
                return False

            with open(zip_path, "rb") as zip_file:
                self.lambda_client.update_function_code(
                    FunctionName=function_name, ZipFile=zip_file.read()
                )

            print(f"✅ Function code updated for {function_name}")
            return True

        except Exception as e:
            print(f"❌ Error updating function code for {function_name}: {e}")
            return False

    def wait_for_function_update(self, function_name: str, timeout: int = 300) -> bool:
        """Wait for function update to complete"""
        import time

        print(f"⏳ Waiting for function update to complete...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = self.lambda_client.get_function(FunctionName=function_name)
                state = response["Configuration"]["State"]

                if state == "Active":
                    print(f"✅ Function {function_name} is now active")
                    return True
                elif state == "Failed":
                    print(f"❌ Function {function_name} update failed")
                    return False
                else:
                    print(f"⏳ Function state: {state}")
                    time.sleep(5)

            except Exception as e:
                print(f"⚠️  Error checking function state: {e}")
                time.sleep(5)

        print(f"⏰ Timeout waiting for function update")
        return False

    def function_code_changed(self, function_name: str, zip_path: str) -> bool:
        """Check if function code has changed by comparing SHA256 hashes"""
        try:
            # Get current function info
            response = self.lambda_client.get_function(FunctionName=function_name)
            current_sha256 = response["Configuration"]["CodeSha256"]

            # Calculate SHA256 of new zip file
            import hashlib

            with open(zip_path, "rb") as f:
                new_sha256 = hashlib.sha256(f.read()).hexdigest()

            # Compare hashes
            changed = current_sha256 != new_sha256

            if changed:
                print(f"🔄 Code changes detected for {function_name}")
                print(f"   Current SHA256: {current_sha256[:12]}...")
                print(f"   New SHA256:     {new_sha256[:12]}...")
            else:
                print(
                    f"✅ No code changes for {function_name} (SHA256: {current_sha256[:12]}...)"
                )

            return changed

        except Exception as e:
            # If we can't check, assume it changed (safe default)
            print(f"⚠️  Could not check code changes for {function_name}: {e}")
            print(f"   Proceeding with deployment as safe default")
            return True

    def deploy_function(self, function_key: str, environment: str) -> bool:
        """Deploy a specific function to STAGING or PROD environment"""
        if function_key not in self.functions:
            print(f"❌ Function key {function_key} not found in configuration")
            return False

        if environment not in self.environments:
            print(f"❌ Environment {environment} not found in configuration")
            print(f"Available environments: {', '.join(self.environments.keys())}")
            print(f"💻 Note: DEV environment is local-only, no deployment needed")
            return False

        function_name = self.functions[function_key]
        env_config = self.environments[environment]
        alias_name = env_config["alias"]

        print(f"🚀 Deploying {function_key} to {environment} environment...")

        # Find the function directory
        function_dir = None
        for root, dirs, files in os.walk("Lambdas"):
            for dir_name in dirs:
                if dir_name == function_key:
                    function_dir = os.path.join(root, dir_name)
                    break
            if function_dir:
                break

        if not function_dir:
            print(f"❌ Function directory not found for {function_key}")
            return False

        # Create deployment package
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            zip_path = tmp_file.name

        try:
            self.create_deployment_package(function_dir, zip_path)

            # Check if function exists
            function_exists = True
            try:
                self.lambda_client.get_function(FunctionName=function_name)
            except self.lambda_client.exceptions.ResourceNotFoundException:
                function_exists = False
                print(f"🆕 Function {function_name} does not exist. Will create it.")

            if function_exists:
                # Function exists, check if code changed
                needs_update = self.function_code_changed(function_name, zip_path)

                if needs_update:
                    # Update function code
                    if not self.update_function_code(function_name, zip_path):
                        return False

                    # Wait for update to complete
                    if not self.wait_for_function_update(function_name):
                        return False

                    # Publish new version
                    version = self.alias_manager.publish_version(
                        function_name, f"Deployed to {environment} environment"
                    )
                else:
                    print(
                        f"⏭️  No changes detected for {function_name}, skipping deployment"
                    )
                    # Get current alias version
                    alias_info = self.alias_manager.get_alias_info(
                        function_name, alias_name
                    )
                    version = alias_info["FunctionVersion"] if alias_info else None
            else:
                # Function doesn't exist, create it
                if not self.create_lambda_function(function_name, zip_path):
                    return False

                # Wait for function to be active
                if not self.wait_for_function_update(function_name):
                    return False

                # Publish initial version
                version = self.alias_manager.publish_version(
                    function_name, f"Initial deployment to {environment} environment"
                )

            if not version:
                return False

            # Update alias
            if not self.alias_manager.create_alias(
                function_name, alias_name, version, env_config["description"]
            ):
                return False

            print(
                f"✅ Successfully deployed {function_key} to {environment} environment"
            )
            print(f"   Function: {function_name}")
            print(f"   Version: {version}")
            print(f"   Alias: {alias_name}")

            return True

        finally:
            # Clean up temporary file
            if os.path.exists(zip_path):
                os.unlink(zip_path)

    def deploy_all_functions(self, environment: str) -> bool:
        """Deploy all functions to STAGING or PROD environment"""
        if environment not in self.environments:
            print(f"❌ Environment {environment} not found in configuration")
            print(f"Available environments: {', '.join(self.environments.keys())}")
            print(f"💻 Note: DEV environment is local-only, no deployment needed")
            return False

        print(f"🚀 Deploying all functions to {environment} environment...")

        success = True
        for function_key in self.functions.keys():
            print(f"\n📋 Processing function: {function_key}")
            if not self.deploy_function(function_key, environment):
                success = False

        return success

    def promote_environment(
        self, function_key: str, source_env: str, target_env: str
    ) -> bool:
        """Promote a function from one environment to another (e.g., STAGING to PROD)"""
        if function_key not in self.functions:
            print(f"❌ Function key {function_key} not found in configuration")
            return False

        if source_env not in self.environments or target_env not in self.environments:
            print(f"❌ Invalid environment: {source_env} or {target_env}")
            print(f"Available environments: {', '.join(self.environments.keys())}")
            return False

        function_name = self.functions[function_key]
        source_alias = self.environments[source_env]["alias"]
        target_alias = self.environments[target_env]["alias"]

        print(f"🔄 Promoting {function_key} from {source_env} to {target_env}...")

        return self.alias_manager.promote_alias(
            function_name, source_alias, target_alias
        )

    def list_deployment_status(self) -> Dict:
        """List the deployment status of all functions"""
        print("📊 Deployment Status Report")
        print("=" * 50)

        result = {}
        for function_key, function_name in self.functions.items():
            print(f"\n📋 Function: {function_key} ({function_name})")

            aliases = self.alias_manager.get_function_aliases(function_name)
            versions = self.alias_manager.get_function_versions(function_name)

            result[function_key] = {
                "function_name": function_name,
                "aliases": aliases,
                "versions": versions,
            }

            # Show alias status
            for env_name, env_config in self.environments.items():
                alias_name = env_config["alias"]
                alias_info = next((a for a in aliases if a["Name"] == alias_name), None)

                if alias_info:
                    print(
                        f"  ✅ {env_name}: {alias_name} → v{alias_info['FunctionVersion']}"
                    )
                else:
                    print(f"  ❌ {env_name}: {alias_name} → Not configured")

            print(f"  💻 DEV: Local testing only (no alias)")

        return result


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("🚀 Lambda Deployer with Alias Management")
        print("")
        print("Usage:")
        print(
            "  python scripts/deploy_with_aliases.py deploy <function_key> <environment>"
        )
        print("  python scripts/deploy_with_aliases.py deploy-all <environment>")
        print(
            "  python scripts/deploy_with_aliases.py promote <function_key> <source_env> <target_env>"
        )
        print("  python scripts/deploy_with_aliases.py status")
        print("")
        print("Environments: STAGING, PROD")
        print("Function Keys:", ", ".join(LAMBDA_FUNCTION_NAMES.keys()))
        print("")
        print("💻 Note: DEV environment is local-only, no deployment needed")
        print("")
        print("Examples:")
        print("  python scripts/deploy_with_aliases.py deploy recieveEmail STAGING")
        print("  python scripts/deploy_with_aliases.py deploy-all STAGING")
        print(
            "  python scripts/deploy_with_aliases.py promote recieveEmail STAGING PROD"
        )
        print("  python scripts/deploy_with_aliases.py status")
        return

    command = sys.argv[1]
    deployer = LambdaDeployer()

    if command == "deploy":
        if len(sys.argv) < 4:
            print("❌ deploy command requires: function_key environment")
            return

        function_key = sys.argv[2]
        environment = sys.argv[3]

        deployer.deploy_function(function_key, environment)

    elif command == "deploy-all":
        if len(sys.argv) < 3:
            print("❌ deploy-all command requires: environment")
            return

        environment = sys.argv[2]
        deployer.deploy_all_functions(environment)

    elif command == "promote":
        if len(sys.argv) != 5:
            print("❌ promote command requires: function_key source_env target_env")
            return

        function_key = sys.argv[2]
        source_env = sys.argv[3]
        target_env = sys.argv[4]

        deployer.promote_environment(function_key, source_env, target_env)

    elif command == "status":
        deployer.list_deployment_status()

    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
