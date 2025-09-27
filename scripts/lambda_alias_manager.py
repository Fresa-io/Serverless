#!/usr/bin/env python3
"""
Lambda Alias Manager
Manages Lambda function aliases for STAGING and PROD environments
DEV environment is local-only, no alias needed
"""

import boto3
import json
import sys
import os
from typing import Dict, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LAMBDA_FUNCTION_NAMES, LAMBDA_ALIASES, DEPLOYMENT_ENV


class LambdaAliasManager:
    def __init__(self, region: str = None):
        """Initialize the Lambda alias manager"""
        # Use environment variable or default region if none provided
        if region is None:
            region = os.environ.get("AWS_REGION") or os.environ.get("CDK_DEFAULT_REGION") or "us-east-1"
        
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.functions = LAMBDA_FUNCTION_NAMES
        self.aliases = LAMBDA_ALIASES
        self.environments = DEPLOYMENT_ENV

    def list_functions(self) -> List[str]:
        """List all Lambda functions"""
        try:
            response = self.lambda_client.list_functions()
            return [func["FunctionName"] for func in response["Functions"]]
        except Exception as e:
            print(f"❌ Error listing functions: {e}")
            return []

    def get_function_versions(self, function_name: str) -> List[Dict]:
        """Get all versions of a Lambda function"""
        try:
            response = self.lambda_client.list_versions_by_function(
                FunctionName=function_name
            )
            return response["Versions"]
        except Exception as e:
            print(f"❌ Error getting versions for {function_name}: {e}")
            return []

    def get_function_aliases(self, function_name: str) -> List[Dict]:
        """Get all aliases of a Lambda function"""
        try:
            response = self.lambda_client.list_aliases(FunctionName=function_name)
            return response["Aliases"]
        except Exception as e:
            print(f"❌ Error getting aliases for {function_name}: {e}")
            return []

    def create_alias(
        self, function_name: str, alias_name: str, version: str, description: str = ""
    ) -> bool:
        """Create or update a Lambda alias"""
        try:
            # Safety check: Verify function exists
            try:
                self.lambda_client.get_function(FunctionName=function_name)
            except self.lambda_client.exceptions.ResourceNotFoundException:
                print(
                    f"❌ Function {function_name} does not exist. Cannot create alias."
                )
                return False

            # Check if alias exists
            try:
                self.lambda_client.get_alias(
                    FunctionName=function_name, Name=alias_name
                )
                # Alias exists, update it
                print(
                    f"🔄 Updating alias {alias_name} for {function_name} to version {version}"
                )
                self.lambda_client.update_alias(
                    FunctionName=function_name,
                    Name=alias_name,
                    FunctionVersion=version,
                    Description=description,
                )
            except self.lambda_client.exceptions.ResourceNotFoundException:
                # Alias doesn't exist, create it
                print(
                    f"🆕 Creating alias {alias_name} for {function_name} pointing to version {version}"
                )
                self.lambda_client.create_alias(
                    FunctionName=function_name,
                    Name=alias_name,
                    FunctionVersion=version,
                    Description=description,
                )

            print(f"✅ Successfully set alias {alias_name} to version {version}")
            return True

        except Exception as e:
            print(
                f"❌ Error creating/updating alias {alias_name} for {function_name}: {e}"
            )
            return False

    def publish_version(
        self, function_name: str, description: str = ""
    ) -> Optional[str]:
        """Publish a new version of a Lambda function"""
        try:
            print(f"📦 Publishing new version for {function_name}...")
            response = self.lambda_client.publish_version(
                FunctionName=function_name, Description=description
            )
            version = response["Version"]
            print(f"✅ Published version {version} for {function_name}")
            return version
        except Exception as e:
            print(f"❌ Error publishing version for {function_name}: {e}")
            return None

    def setup_aliases_for_function(
        self, function_name: str, version: str = None
    ) -> bool:
        """Setup STAGING and PROD aliases for a function"""
        if function_name not in self.functions.values():
            print(f"⚠️  Function {function_name} not found in configuration")
            return False

        # If no version specified, publish a new one
        if not version:
            version = self.publish_version(function_name, "Auto-published version")
            if not version:
                return False

        success = True

        # Setup STAGING and PROD aliases only
        for env_name, env_config in self.environments.items():
            alias_name = env_config["alias"]
            description = env_config["description"]

            if not self.create_alias(function_name, alias_name, version, description):
                success = False

        return success

    def setup_all_aliases(self, version: str = None) -> bool:
        """Setup aliases for all configured functions"""
        print("🚀 Setting up aliases for all Lambda functions...")
        print("📝 Note: DEV environment is local-only, no alias needed")

        success = True
        for func_key, func_name in self.functions.items():
            print(f"\n📋 Processing function: {func_name}")
            if not self.setup_aliases_for_function(func_name, version):
                success = False

        return success

    def promote_alias(
        self, function_name: str, source_alias: str, target_alias: str
    ) -> bool:
        """Promote a function from one alias to another (e.g., STAGING to PROD)"""
        try:
            # Get the version that the source alias points to
            source_response = self.lambda_client.get_alias(
                FunctionName=function_name, Name=source_alias
            )
            version = source_response["FunctionVersion"]

            # Update the target alias to point to the same version
            target_config = self.environments.get(target_alias.upper(), {})
            description = target_config.get(
                "description", f"Promoted from {source_alias}"
            )

            return self.create_alias(function_name, target_alias, version, description)

        except Exception as e:
            print(
                f"❌ Error promoting alias {source_alias} to {target_alias} for {function_name}: {e}"
            )
            return False

    def get_alias_info(self, function_name: str, alias_name: str) -> Optional[Dict]:
        """Get information about a specific alias"""
        try:
            response = self.lambda_client.get_alias(
                FunctionName=function_name, Name=alias_name
            )
            return response
        except Exception as e:
            print(f"❌ Error getting alias info for {function_name}:{alias_name}: {e}")
            return None

    def list_all_aliases(self) -> Dict:
        """List all aliases for all functions"""
        result = {}

        for func_key, func_name in self.functions.items():
            print(f"\n📋 Function: {func_name}")
            aliases = self.get_function_aliases(func_name)
            versions = self.get_function_versions(func_name)

            result[func_name] = {"aliases": aliases, "versions": versions}

            print(f"  📌 Versions: {len(versions)}")
            for version in versions[-5:]:  # Show last 5 versions
                print(
                    f"    - {version['Version']}: {version.get('Description', 'No description')}"
                )

            print(f"  🏷️  Aliases: {len(aliases)}")
            for alias in aliases:
                print(
                    f"    - {alias['Name']} → {alias['FunctionVersion']}: {alias.get('Description', 'No description')}"
                )

            print(f"  💻 DEV: Local testing only (no alias)")

        return result

    def rollback_to_previous_version(self, function_name: str, alias_name: str) -> bool:
        """Rollback an alias to the previous version"""
        try:
            # Get all versions
            versions = self.get_function_versions(function_name)
            if len(versions) < 2:
                print(
                    f"❌ Function {function_name} has insufficient versions for rollback"
                )
                return False

            # Get current alias version
            current_alias = self.get_alias_info(function_name, alias_name)
            if not current_alias:
                print(f"❌ Alias {alias_name} not found for {function_name}")
                return False

            current_version = current_alias["FunctionVersion"]
            print(f"📋 Current {alias_name} points to version {current_version}")

            # Find previous version (skip $LATEST)
            non_latest_versions = [v for v in versions if v["Version"] != "$LATEST"]
            non_latest_versions.sort(key=lambda x: int(x["Version"]))

            if len(non_latest_versions) < 2:
                print(f"❌ Not enough numbered versions for rollback")
                return False

            # Find previous version
            current_idx = None
            for i, version in enumerate(non_latest_versions):
                if version["Version"] == current_version:
                    current_idx = i
                    break

            if current_idx is None or current_idx == 0:
                print(f"❌ Cannot determine previous version")
                return False

            previous_version = non_latest_versions[current_idx - 1]["Version"]
            print(
                f"🔄 Rolling back {alias_name} from version {current_version} to {previous_version}"
            )

            # Update alias to previous version
            return self.create_alias(
                function_name,
                alias_name,
                previous_version,
                f"Rollback from {current_version} to {previous_version}",
            )

        except Exception as e:
            print(f"❌ Error rolling back {function_name}:{alias_name}: {e}")
            return False

    def set_alias_to_version(
        self, function_name: str, alias_name: str, target_version: str
    ) -> bool:
        """Set an alias to a specific version"""
        try:
            # Verify target version exists
            versions = self.get_function_versions(function_name)
            version_numbers = [v["Version"] for v in versions]

            if target_version not in version_numbers:
                print(f"❌ Version {target_version} not found for {function_name}")
                print(f"Available versions: {', '.join(version_numbers)}")
                return False

            return self.create_alias(
                function_name,
                alias_name,
                target_version,
                f"Manually set to version {target_version}",
            )

        except Exception as e:
            print(
                f"❌ Error setting {function_name}:{alias_name} to version {target_version}: {e}"
            )
            return False


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("🚀 Lambda Alias Manager")
        print("")
        print("Usage:")
        print(
            "  python scripts/lambda_alias_manager.py setup [function_name] [version]"
        )
        print(
            "  python scripts/lambda_alias_manager.py promote <function_name> <source_alias> <target_alias>"
        )
        print(
            "  python scripts/lambda_alias_manager.py rollback <function_name> <environment>"
        )
        print(
            "  python scripts/lambda_alias_manager.py set-version <function_name> <environment> <version>"
        )
        print("  python scripts/lambda_alias_manager.py list")
        print(
            "  python scripts/lambda_alias_manager.py info <function_name> <alias_name>"
        )
        print("")
        print("Examples:")
        print("  python scripts/lambda_alias_manager.py setup")
        print("  python scripts/lambda_alias_manager.py setup recieveEmail")
        print(
            "  python scripts/lambda_alias_manager.py promote recieveEmail staging prod"
        )
        print("  python scripts/lambda_alias_manager.py rollback userLogin prod")
        print("  python scripts/lambda_alias_manager.py set-version userLogin prod 3")
        print("  python scripts/lambda_alias_manager.py list")
        print("")
        print("📝 Note: DEV environment is local-only, no alias needed")
        return

    command = sys.argv[1]
    manager = LambdaAliasManager()

    if command == "setup":
        function_name = sys.argv[2] if len(sys.argv) > 2 else None
        version = sys.argv[3] if len(sys.argv) > 3 else None

        if function_name:
            manager.setup_aliases_for_function(function_name, version)
        else:
            manager.setup_all_aliases(version)

    elif command == "promote":
        if len(sys.argv) != 5:
            print(
                "❌ promote command requires: function_name source_alias target_alias"
            )
            return

        function_name = sys.argv[2]
        source_alias = sys.argv[3]
        target_alias = sys.argv[4]

        manager.promote_alias(function_name, source_alias, target_alias)

    elif command == "list":
        manager.list_all_aliases()

    elif command == "info":
        if len(sys.argv) != 4:
            print("❌ info command requires: function_name alias_name")
            return

        function_name = sys.argv[2]
        alias_name = sys.argv[3]

        info = manager.get_alias_info(function_name, alias_name)
        if info:
            print(json.dumps(info, indent=2, default=str))

    elif command == "rollback":
        if len(sys.argv) != 4:
            print("❌ rollback command requires: function_name environment")
            return

        function_name = sys.argv[2]
        environment = sys.argv[3].upper()

        # Map environment to alias name
        env_to_alias = {"STAGING": "staging", "PROD": "prod", "PRODUCTION": "prod"}
        alias_name = env_to_alias.get(environment)

        if not alias_name:
            print(f"❌ Invalid environment: {environment}")
            print("Valid environments: STAGING, PROD")
            return

        manager.rollback_to_previous_version(function_name, alias_name)

    elif command == "set-version":
        if len(sys.argv) != 5:
            print("❌ set-version command requires: function_name environment version")
            return

        function_name = sys.argv[2]
        environment = sys.argv[3].upper()
        target_version = sys.argv[4]

        # Map environment to alias name
        env_to_alias = {"STAGING": "staging", "PROD": "prod", "PRODUCTION": "prod"}
        alias_name = env_to_alias.get(environment)

        if not alias_name:
            print(f"❌ Invalid environment: {environment}")
            print("Valid environments: STAGING, PROD")
            return

        manager.set_alias_to_version(function_name, alias_name, target_version)

    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
