#!/usr/bin/env python3
"""
Environment Variable Manager for Lambda Functions
Manages environment variables across STAGING and PROD environments
"""

import boto3
import json
import sys
import os
from typing import Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LAMBDA_FUNCTION_NAMES, DEPLOYMENT_ENV
from utils.config_loader import setup_aws_environment


class EnvironmentManager:
    def __init__(self, region: str = None):
        """Initialize the environment manager"""
        # Setup AWS credentials from environment variables
        setup_aws_environment()

        if region is None:
            region = os.environ.get("AWS_REGION", "us-east-1")
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.functions = LAMBDA_FUNCTION_NAMES
        self.environments = DEPLOYMENT_ENV

    def get_function_environment_variables(self, function_name: str) -> Dict[str, str]:
        """Get current environment variables for a function"""
        try:
            response = self.lambda_client.get_function_configuration(
                FunctionName=function_name
            )
            return response.get("Environment", {}).get("Variables", {})
        except Exception as e:
            print(f"❌ Error getting environment variables for {function_name}: {e}")
            return {}

    def update_function_environment_variables(
        self, function_name: str, env_vars: Dict[str, str]
    ) -> bool:
        """Update environment variables for a function"""
        try:
            self.lambda_client.update_function_configuration(
                FunctionName=function_name, Environment={"Variables": env_vars}
            )
            print(f"✅ Updated environment variables for {function_name}")
            return True
        except Exception as e:
            print(f"❌ Error updating environment variables for {function_name}: {e}")
            return False

    def get_alias_environment_variables(
        self, function_name: str, alias_name: str
    ) -> Dict[str, str]:
        """Get environment variables for a specific alias"""
        try:
            response = self.lambda_client.get_function_configuration(
                FunctionName=f"{function_name}:{alias_name}"
            )
            return response.get("Environment", {}).get("Variables", {})
        except Exception as e:
            print(
                f"❌ Error getting environment variables for {function_name}:{alias_name}: {e}"
            )
            return {}

    def update_alias_environment_variables(
        self, function_name: str, alias_name: str, env_vars: Dict[str, str]
    ) -> bool:
        """Update environment variables for a specific alias"""
        try:
            # Get current configuration
            current_config = self.lambda_client.get_function_configuration(
                FunctionName=function_name
            )

            # Update the function with new environment variables
            self.lambda_client.update_function_configuration(
                FunctionName=function_name, Environment={"Variables": env_vars}
            )

            print(f"✅ Updated environment variables for {function_name}:{alias_name}")
            return True
        except Exception as e:
            print(
                f"❌ Error updating environment variables for {function_name}:{alias_name}: {e}"
            )
            return False

    def setup_environment_specific_variables(
        self, function_name: str, environment: str
    ) -> bool:
        """Setup environment-specific variables for a function"""
        if environment not in self.environments:
            print(f"❌ Environment {environment} not found")
            return False

        # Define environment-specific variables
        env_configs = {
            "STAGING": {
                "COGNITO_CLIENT_ID": "5st6t5kci95r53btoro9du83f3",  # Your current values
                "COGNITO_USER_POOL_ID": "us-east-1_aSNl9TDUl",
                "DYNAMODB_TABLE_NAME": "VerificationCodes",
                "CODE_EXPIRATION_MINUTES": "5",
                "ENVIRONMENT": "staging",
            },
            "PROD": {
                "COGNITO_CLIENT_ID": "5st6t5kci95r53btoro9du83f3",  # Same for now, but you can change
                "COGNITO_USER_POOL_ID": "us-east-1_aSNl9TDUl",
                "DYNAMODB_TABLE_NAME": "VerificationCodes",
                "CODE_EXPIRATION_MINUTES": "5",
                "ENVIRONMENT": "production",
            },
        }

        env_vars = env_configs.get(environment, {})
        if not env_vars:
            print(f"❌ No configuration found for environment {environment}")
            return False

        return self.update_function_environment_variables(function_name, env_vars)

    def list_all_environment_variables(self) -> Dict[str, Dict[str, str]]:
        """List environment variables for all functions"""
        results = {}
        for function_key, function_name in self.functions.items():
            print(f"📋 Getting environment variables for {function_name}...")
            env_vars = self.get_function_environment_variables(function_name)
            results[function_name] = env_vars

            # Also check aliases
            for env_name, env_config in self.environments.items():
                alias_name = env_config["alias"]
                alias_env_vars = self.get_alias_environment_variables(
                    function_name, alias_name
                )
                if alias_env_vars:
                    results[f"{function_name}:{alias_name}"] = alias_env_vars

        return results

    def sync_environment_variables(self, function_name: str) -> bool:
        """Sync environment variables across all aliases for a function"""
        print(f"🔄 Syncing environment variables for {function_name}...")

        # Get current function environment variables
        current_env_vars = self.get_function_environment_variables(function_name)

        if not current_env_vars:
            print(f"❌ No environment variables found for {function_name}")
            return False

        success = True
        for env_name, env_config in self.environments.items():
            alias_name = env_config["alias"]
            print(f"📝 Syncing to {alias_name} alias...")

            # Add environment-specific variables
            env_vars = current_env_vars.copy()
            env_vars["ENVIRONMENT"] = alias_name

            if not self.update_alias_environment_variables(
                function_name, alias_name, env_vars
            ):
                success = False

        return success


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python environment_manager.py <command> [args...]")
        print("Commands:")
        print("  list [function_name]           - List environment variables")
        print("  update <function> <env>         - Update environment variables")
        print("  sync <function_name>           - Sync variables across aliases")
        print("  setup <function> <environment> - Setup environment-specific variables")
        return

    command = sys.argv[1]
    manager = EnvironmentManager()

    if command == "list":
        if len(sys.argv) > 2:
            function_name = sys.argv[2]
            env_vars = manager.get_function_environment_variables(function_name)
            print(f"Environment variables for {function_name}:")
            for key, value in env_vars.items():
                print(f"  {key}: {value}")
        else:
            all_vars = manager.list_all_environment_variables()
            for func_name, env_vars in all_vars.items():
                print(f"\n{func_name}:")
                for key, value in env_vars.items():
                    print(f"  {key}: {value}")

    elif command == "update":
        if len(sys.argv) != 4:
            print("❌ update command requires: function_name environment")
            return

        function_name = sys.argv[2]
        environment = sys.argv[3].upper()

        if manager.setup_environment_specific_variables(function_name, environment):
            print(f"✅ Updated {function_name} for {environment}")
        else:
            print(f"❌ Failed to update {function_name} for {environment}")

    elif command == "sync":
        if len(sys.argv) != 3:
            print("❌ sync command requires: function_name")
            return

        function_name = sys.argv[2]
        if manager.sync_environment_variables(function_name):
            print(f"✅ Synced environment variables for {function_name}")
        else:
            print(f"❌ Failed to sync environment variables for {function_name}")

    elif command == "setup":
        if len(sys.argv) != 4:
            print("❌ setup command requires: function_name environment")
            return

        function_name = sys.argv[2]
        environment = sys.argv[3].upper()

        if manager.setup_environment_specific_variables(function_name, environment):
            print(f"✅ Setup {function_name} for {environment}")
        else:
            print(f"❌ Failed to setup {function_name} for {environment}")

    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
