#!/usr/bin/env python3
"""
Fresa SES Template Remover
Based on the original remove_template.py script
"""

import boto3
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.aws_utils import get_aws_account_info, print_aws_info


def delete_ses_template(template_name):
    """
    Deletes an email template in Amazon SES.

    Args:
        template_name (str): The name of the template to delete.

    Returns:
        dict: The response from the SES client, or None if deletion failed.
    """
    ses_client = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    
    try:
        response = ses_client.delete_template(
            TemplateName=template_name
        )
        print(f"✅ Successfully deleted template: {template_name}")
        return response
    except ses_client.exceptions.TemplateDoesNotExistException:
        print(f"⚠️  Template '{template_name}' does not exist. No action taken.")
        return None
    except Exception as e:
        print(f"❌ Error deleting template {template_name}: {e}")
        return None


def main():
    """Main function to delete templates"""
    print("🍓 Fresa SES Template Remover")
    print("=" * 40)
    
    # Print AWS info
    print_aws_info()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python remove_template.py <template_name>")
        print("  python remove_template.py fresa-welcome-template")
        print("  python remove_template.py fresa-verificacion-template")
        sys.exit(1)
    
    template_name = sys.argv[1]
    
    print(f"🗑️  Deleting template: {template_name}")
    
    result = delete_ses_template(template_name)
    if result:
        print(f"\n🎉 Template '{template_name}' deleted successfully!")
    else:
        print(f"\n❌ Failed to delete template '{template_name}'")


if __name__ == '__main__':
    main()
