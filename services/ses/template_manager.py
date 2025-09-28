#!/usr/bin/env python3
"""
SES Template Manager
Handles creation, update, and removal of SES email templates
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
    """Create default SES templates for the application"""
    manager = SESTemplateManager()
    
    # Fresa verification template
    verification_template = {
        'template_name': 'fresa-verificacion-template',
        'subject': 'Verificación de Email - Fresa',
        'html_content': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Verificación de Email</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2c3e50;">🍓 Fresa</h1>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #2c3e50; margin-top: 0;">Verificación de Email</h2>
                <p>Hola,</p>
                <p>Para completar tu registro en Fresa, por favor verifica tu dirección de email haciendo clic en el siguiente enlace:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{{verification_link}}" 
                       style="background-color: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verificar Email
                    </a>
                </div>
                
                <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                <p style="word-break: break-all; color: #666;">{{verification_link}}</p>
                
                <p>Este enlace expirará en 24 horas.</p>
            </div>
            
            <div style="text-align: center; color: #666; font-size: 12px;">
                <p>Si no solicitaste este email, puedes ignorarlo de forma segura.</p>
                <p>© 2025 Fresa. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        ''',
        'text_content': '''
        Verificación de Email - Fresa
        
        Hola,
        
        Para completar tu registro en Fresa, por favor verifica tu dirección de email visitando el siguiente enlace:
        
        {{verification_link}}
        
        Este enlace expirará en 24 horas.
        
        Si no solicitaste este email, puedes ignorarlo de forma segura.
        
        © 2025 Fresa. Todos los derechos reservados.
        '''
    }
    
    # Create the template
    success = manager.create_or_update_template(
        verification_template['template_name'],
        verification_template['subject'],
        verification_template['html_content'],
        verification_template['text_content']
    )
    
    if success:
        print("✅ Default SES templates created successfully")
    else:
        print("❌ Failed to create default SES templates")
    
    return success


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python services/ses/template_manager.py list")
        print("  python services/ses/template_manager.py get <template_name>")
        print("  python services/ses/template_manager.py create <template_name> <subject> <html_content> [text_content]")
        print("  python services/ses/template_manager.py update <template_name> <subject> <html_content> [text_content]")
        print("  python services/ses/template_manager.py delete <template_name>")
        print("  python services/ses/template_manager.py create-defaults")
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
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
