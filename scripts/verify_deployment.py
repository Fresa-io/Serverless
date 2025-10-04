#!/usr/bin/env python3
"""
Deployment Verification Script
Verifies the current state of Lambda functions in your AWS account
"""

import boto3
import json
import sys
import os
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LAMBDA_FUNCTION_NAMES
from utils.aws_utils import get_aws_account_info, print_aws_info
from utils.config_loader import setup_aws_environment


def verify_lambda_functions():
    """Verify all Lambda functions are deployed and accessible"""
    print("🔍 Verifying Lambda Functions Deployment")
    print("=" * 50)

    # Setup AWS credentials from environment variables
    setup_aws_environment()
    
    lambda_client = boto3.client("lambda")
    results = {}

    for function_key, function_name in LAMBDA_FUNCTION_NAMES.items():
        print(f"\n📋 Checking {function_key} ({function_name})...")

        try:
            # Get function details
            response = lambda_client.get_function(FunctionName=function_name)
            config = response["Configuration"]

            results[function_key] = {
                "exists": True,
                "arn": config["FunctionArn"],
                "runtime": config["Runtime"],
                "handler": config["Handler"],
                "state": config["State"],
                "last_modified": config["LastModified"],
                "role": config["Role"],
            }

            print(f"  ✅ Function exists")
            print(f"     ARN: {config['FunctionArn']}")
            print(f"     Runtime: {config['Runtime']}")
            print(f"     Handler: {config['Handler']}")
            print(f"     State: {config['State']}")
            print(f"     Last Modified: {config['LastModified']}")

            # Try to get aliases
            try:
                aliases_response = lambda_client.list_aliases(
                    FunctionName=function_name
                )
                aliases = aliases_response.get("Aliases", [])
                results[function_key]["aliases"] = aliases

                if aliases:
                    print(f"     Aliases: {len(aliases)} found")
                    for alias in aliases:
                        print(f"       - {alias['Name']} → v{alias['FunctionVersion']}")
                else:
                    print(f"     Aliases: None configured")

            except Exception as e:
                print(f"     ⚠️  Cannot check aliases: {e}")
                results[function_key]["aliases"] = []

        except lambda_client.exceptions.ResourceNotFoundException:
            results[function_key] = {"exists": False}
            print(f"  ❌ Function does not exist")

        except Exception as e:
            results[function_key] = {"exists": False, "error": str(e)}
            print(f"  ❌ Error checking function: {e}")

    return results


def print_summary(results: Dict):
    """Print deployment summary"""
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 50)

    total_functions = len(results)
    existing_functions = sum(1 for r in results.values() if r.get("exists", False))

    print(f"Total functions configured: {total_functions}")
    print(f"Functions deployed: {existing_functions}")
    print(f"Functions missing: {total_functions - existing_functions}")

    if existing_functions == total_functions:
        print("\n🎉 All Lambda functions are deployed and accessible!")
        print("\n📝 Next Steps:")
        print("1. Update GitHub Actions secrets with your new AWS credentials")
        print("2. Test the deployment pipeline")
        print("3. Configure aliases for STAGING and PROD environments")
    else:
        print(
            f"\n⚠️  {total_functions - existing_functions} functions need to be deployed"
        )

        missing_functions = [
            k for k, v in results.items() if not v.get("exists", False)
        ]
        print(f"Missing functions: {', '.join(missing_functions)}")


def main():
    """Main function"""
    print("🚀 Lambda Functions Deployment Verification")

    # Print current AWS configuration
    account_info = print_aws_info()
    if not account_info:
        print("❌ Cannot detect AWS configuration. Please check your credentials.")
        sys.exit(1)

    print()

    try:
        results = verify_lambda_functions()
        print_summary(results)

        # Save results to file
        with open("deployment_status.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Detailed results saved to: deployment_status.json")

    except Exception as e:
        print(f"❌ Error during verification: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
