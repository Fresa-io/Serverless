#!/usr/bin/env python3
"""
Fresa SES Template Manager
Integrates the user's original SES template scripts into the modular system
"""

import boto3
import json
import sys
import os
from typing import Dict, List, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.aws_utils import get_aws_account_info, print_aws_info

# Import the user's original scripts
from services.ses.create_verification_template import create_ses_template_with_logo
from services.ses.create_welcome_template import create_welcome_template_with_logo, get_gendered_template_data
from services.ses.remove_template import delete_ses_template
from services.ses.test_aws_credentials import test_aws_credentials


class SESTemplateManager:
    """Manages SES email templates"""
    
    def __init__(self, region: str = None):
        """Initialize SES template manager"""
        if region is None:
            region = os.environ.get("AWS_REGION") or "us-east-1"
        
        self.ses_client = boto3.client('ses', region_name=region)
        self.region = region
    
    def list_templates(self) -> List[Dict]:
        """List all SES templates"""
        try:
            response = self.ses_client.list_templates()
            return response.get('TemplatesMetadata', [])
        except Exception as e:
            print(f"❌ Error listing templates: {e}")
            return []
    
    def get_template(self, template_name: str) -> Optional[Dict]:
        """Get a specific template"""
        try:
            response = self.ses_client.get_template(TemplateName=template_name)
            return response.get('Template', {})
        except Exception as e:
            print(f"❌ Error getting template {template_name}: {e}")
            return None
    
    def create_template(self, template_name: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Create a new SES template"""
        try:
            template_data = {
                'TemplateName': template_name,
                'SubjectPart': subject,
                'HtmlPart': html_content
            }
            
            if text_content:
                template_data['TextPart'] = text_content
            
            self.ses_client.create_template(Template=template_data)
            print(f"✅ Created SES template: {template_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating template {template_name}: {e}")
            return False
    
    def update_template(self, template_name: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Update an existing SES template"""
        try:
            template_data = {
                'TemplateName': template_name,
                'SubjectPart': subject,
                'HtmlPart': html_content
            }
            
            if text_content:
                template_data['TextPart'] = text_content
            
            self.ses_client.update_template(Template=template_data)
            print(f"✅ Updated SES template: {template_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating template {template_name}: {e}")
            return False
    
    def delete_template(self, template_name: str) -> bool:
        """Delete an SES template"""
        try:
            self.ses_client.delete_template(TemplateName=template_name)
            print(f"✅ Deleted SES template: {template_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting template {template_name}: {e}")
            return False
    
    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists"""
        try:
            self.ses_client.get_template(TemplateName=template_name)
            return True
        except:
            return False
    
    def create_or_update_template(self, template_name: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Create template if it doesn't exist, otherwise update it"""
        if self.template_exists(template_name):
            return self.update_template(template_name, subject, html_content, text_content)
        else:
            return self.create_template(template_name, subject, html_content, text_content)


def load_template_from_file(template_path: str) -> Dict:
    """Load template configuration from JSON file"""
    try:
        with open(template_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading template from {template_path}: {e}")
        return {}


def create_default_templates():
    """Create default SES templates using the user's original scripts"""
    print("🍓 Creating Fresa SES Templates")
    print("=" * 40)
    
    # Print AWS info
    print_aws_info()
    
    success = True
    
    # Create verification template using user's script
    print("\n📧 Creating verification template...")
    verification_result = create_ses_template_with_logo(
        template_name='fresa-verificacion-template',
        logo_url='https://fresaassets.s3.us-east-1.amazonaws.com/fresaicon.png'
    )
    
    if verification_result:
        print("✅ Verification template created successfully")
    else:
        print("❌ Failed to create verification template")
        success = False
    
    # Create welcome template using user's script
    print("\n📧 Creating welcome template...")
    welcome_result = create_welcome_template_with_logo(
        template_name='fresa-welcome-template',
        logo_url='https://fresaassets.s3.us-east-1.amazonaws.com/fresaicon.png'
    )
    
    if welcome_result:
        print("✅ Welcome template created successfully")
    else:
        print("❌ Failed to create welcome template")
        success = False
    
    if success:
        print("\n🎉 All Fresa SES templates created successfully!")
    else:
        print("\n❌ Some templates failed to create")
    
    return success


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("🍓 Fresa SES Template Manager")
        print("=" * 40)
        print("Usage:")
        print("  python services/ses/template_manager.py list")
        print("  python services/ses/template_manager.py get <template_name>")
        print("  python services/ses/template_manager.py create <template_name> <subject> <html_content> [text_content]")
        print("  python services/ses/template_manager.py update <template_name> <subject> <html_content> [text_content]")
        print("  python services/ses/template_manager.py delete <template_name>")
        print("  python services/ses/template_manager.py create-defaults")
        print("  python services/ses/template_manager.py create-verification")
        print("  python services/ses/template_manager.py create-welcome")
        print("  python services/ses/template_manager.py test-credentials")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = SESTemplateManager()
    
    # Print AWS info
    print("🔍 SES Template Manager")
    account_info = print_aws_info()
    if not account_info:
        print("❌ Cannot detect AWS configuration. Please check your credentials.")
        sys.exit(1)
    print()
    
    if command == "list":
        templates = manager.list_templates()
        print(f"📋 Found {len(templates)} SES templates:")
        for template in templates:
            print(f"   - {template['Name']} (Created: {template['CreatedTimestamp']})")
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("❌ Template name required")
            sys.exit(1)
        
        template_name = sys.argv[2]
        template = manager.get_template(template_name)
        if template:
            print(f"📄 Template: {template_name}")
            print(f"   Subject: {template.get('SubjectPart', 'N/A')}")
            print(f"   HTML Content: {len(template.get('HtmlPart', ''))} characters")
            print(f"   Text Content: {len(template.get('TextPart', ''))} characters")
        else:
            print(f"❌ Template {template_name} not found")
    
    elif command == "create":
        if len(sys.argv) < 5:
            print("❌ create command requires: template_name subject html_content [text_content]")
            sys.exit(1)
        
        template_name = sys.argv[2]
        subject = sys.argv[3]
        html_content = sys.argv[4]
        text_content = sys.argv[5] if len(sys.argv) > 5 else None
        
        manager.create_template(template_name, subject, html_content, text_content)
    
    elif command == "update":
        if len(sys.argv) < 5:
            print("❌ update command requires: template_name subject html_content [text_content]")
            sys.exit(1)
        
        template_name = sys.argv[2]
        subject = sys.argv[3]
        html_content = sys.argv[4]
        text_content = sys.argv[5] if len(sys.argv) > 5 else None
        
        manager.update_template(template_name, subject, html_content, text_content)
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Template name required")
            sys.exit(1)
        
        template_name = sys.argv[2]
        manager.delete_template(template_name)
    
    elif command == "create-defaults":
        create_default_templates()
    
    elif command == "create-verification":
        print("📧 Creating verification template...")
        result = create_ses_template_with_logo(
            template_name='fresa-verificacion-template',
            logo_url='https://fresaassets.s3.us-east-1.amazonaws.com/fresaicon.png'
        )
        if result:
            print("✅ Verification template created successfully!")
        else:
            print("❌ Failed to create verification template")
    
    elif command == "create-welcome":
        print("📧 Creating welcome template...")
        result = create_welcome_template_with_logo(
            template_name='fresa-welcome-template',
            logo_url='https://fresaassets.s3.us-east-1.amazonaws.com/fresaicon.png'
        )
        if result:
            print("✅ Welcome template created successfully!")
        else:
            print("❌ Failed to create welcome template")
    
    elif command == "test-credentials":
        test_aws_credentials()
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
