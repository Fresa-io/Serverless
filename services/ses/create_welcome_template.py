#!/usr/bin/env python3
"""
Fresa SES Welcome Template Creator
Based on the original create_template_welcome.py script
"""

import boto3
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.aws_utils import get_aws_account_info, print_aws_info


def create_welcome_template_with_logo(template_name, logo_url):
    """
    Create or update a welcome email template with a logo
    """
    subject = 'Fresa: ¡{{greeting}} {{name}}! 🎉'
    
    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{{{greeting}}}} a Fresa</title>
<style>
    body {{ 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
        margin: 0;
        padding: 0;
        background-color: #f7fafc;
    }}
    .container {{
        max-width: 600px;
        margin: 20px auto;
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }}
    .header {{
        background-color: #ffffff;
        padding: 24px 24px 10px 24px;
        text-align: center;
    }}
    .logo {{
        max-width: 65px;
        height: auto;
        display: block;
        margin: 0 auto;
    }}
    .content {{
        padding: 12px 24px 32px 24px;
        color: #1a202c;
        line-height: 1.6;
    }}
    h1 {{
        color: #2d3748;
        margin: 0 0 24px 0;
        font-size: 28px;
        text-align: center;
    }}
    .welcome-box {{
        background-color: #fde8ec;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        margin: 24px 0;
    }}
    .welcome-message {{
        font-size: 18px;
        font-weight: 600;
        color: #ef5b77;
        margin-bottom: 12px;
    }}
    .feature-list {{
        background-color: #f7fafc;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
    }}
    .feature-item {{
        display: flex;
        align-items: center;
        margin: 12px 0;
        color: #2d3748;
    }}
    .feature-icon {{
        font-size: 20px;
        margin-right: 12px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
    }}
    .footer {{
        text-align: center;
        padding: 12px 24px;
        background-color: #f7fafc;
        color: #718096;
        font-size: 14px;
    }}
</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{logo_url}" 
                 class="logo" 
                 alt="Logo Fresa">
        </div>
        <div class="content">
            <h1>¡Hola {{{{name}}}}! 👋</h1>
            
            <div class="welcome-box">
                <div class="welcome-message">¡{{{{greeting}}}} a la familia Fresa!</div>
                <p style="margin: 0; color: #4a5568;">{{{{excitement_message}}}}</p>
            </div>
            
            <div class="feature-list">
                <h3 style="color: #2d3748; margin-top: 0;">¿Qué puedes hacer en Fresa?</h3>
                <div class="feature-item">
                    <div class="feature-icon">🎁</div>
                    <span>Gana puntos con cada compra que realices</span>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🏆</div>
                    <span>Canjea tus puntos por increíbles premios</span>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">💰</div>
                    <span>Accede a descuentos exclusivos y ofertas especiales</span>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">📱</div>
                    <span>Rastrea tus puntos y premios en tiempo real</span>
                </div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <p style="margin: 0; color: #2d3748; font-weight: 600; font-size: 20px;">¡Empieza a Ahorrar!</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #718096; font-size: 14px;">
                <p><strong>¿Necesitas ayuda?</strong> Contáctanos en support@fresa.live</p>
                <p>© 2025 Fresa. Todos los derechos reservados.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    text_body = """¡Hola {{name}}!

¡{{greeting}} a la familia Fresa!

{{excitement_message}}.

¿Qué puedes hacer en Fresa?
🎁 Gana puntos con cada compra que realices
🏆 Canjea tus puntos por increíbles premios
💰 Accede a descuentos exclusivos y ofertas especiales
📱 Rastrea tus puntos y premios en tiempo real

¡Empieza a Ahorrar!

¡Gracias por unirte a nuestra comunidad!

El Equipo de Fresa
support@fresa.live
© 2025 Fresa. Todos los derechos reservados.
"""

    ses_client = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    
    try:
        response = ses_client.update_template(
            Template={
                'TemplateName': template_name,
                'SubjectPart': subject,
                'HtmlPart': html_body,
                'TextPart': text_body
            }
        )
        print(f"✅ Welcome template actualizado con éxito: {template_name}")
        return response
    except ses_client.exceptions.TemplateDoesNotExistException:
        print(f"📝 Template '{template_name}' no existe. Creándolo...")
        try:
            response = ses_client.create_template(
                Template={
                    'TemplateName': template_name,
                    'SubjectPart': subject,
                    'HtmlPart': html_body,
                    'TextPart': text_body
                }
            )
            print(f"✅ Welcome template creado con éxito: {template_name}")
            return response
        except Exception as e:
            print(f"❌ Error al crear welcome template {template_name}: {e}")
            return None
    except Exception as e:
        print(f"❌ Error al actualizar welcome template {template_name}: {e}")
        return None


def get_gendered_template_data(name, gender):
    """
    Helper function to generate gender-appropriate template data
    """
    # Common data for all users
    template_data = {
        'name': name,
        'excitement_message': 'Estamos emocionados de tenerte con nosotros'
    }
    
    # Gender-specific customizations
    if gender.lower() == 'female':
        template_data.update({
            'greeting': 'Bienvenida'
        })
    else:  # default to male
        template_data.update({
            'greeting': 'Bienvenido'
        })
    
    return template_data


def main():
    """Main function to create welcome template"""
    print("🍓 Fresa SES Welcome Template Creator")
    print("=" * 50)
    
    # Print AWS info
    print_aws_info()
    
    # Use the EXACT S3 URL format from your original script
    logo_url = 'https://fresaassets.s3.us-east-1.amazonaws.com/fresaicon.png'
    
    # Create the welcome template
    result = create_welcome_template_with_logo(
        template_name='fresa-welcome-template',
        logo_url=logo_url
    )
    
    if result:
        print("\n🎉 Welcome template created/updated successfully!")
    else:
        print("\n❌ Failed to create/update welcome template")


if __name__ == '__main__':
    main()
