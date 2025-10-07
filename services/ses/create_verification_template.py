#!/usr/bin/env python3
"""
Fresa SES Verification Template Creator
Based on the original create_template.py script
"""

import boto3
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from utils.aws_utils import get_aws_account_info, print_aws_info


def create_ses_template_with_logo(template_name, logo_url):
    """
    Create or update a verification email template with a logo
    """
    subject = "Fresa: Tu Código de Verificación: {{verificationCode}}"

    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Verificación de Correo</title>
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
    }}
    h1 {{
        color: #2d3748;
        margin: 0 0 24px 0;
        font-size: 24px;
        text-align: center;
    }}
    .code-box {{
        background-color: #fde8ec;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        margin: 24px 0;
        font-size: 20px;
        font-weight: 600;
        color: #ef5b77;
    }}
    .footer {{
        text-align: center;
        padding: 24px;
        background-color: #f7fafc;
        color: #718096;
        font-size: 14px;
    }}
    .expiry {{
        text-align: center;
        color: #718096;
        margin: 16px 0;
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
            <h1>Verifica Tu Cuenta</h1>
            <div class="code-box">
                {{{{verificationCode}}}}
            </div>
            <p class="expiry">Este código expira en {{{{expirationMinutes}}}} minutos</p>
            <p style="text-align: center; color: #718096; margin: 16px 0;">Si no solicitaste este código, por favor ignora este mensaje.</p>
        </div>
        <div class="footer">
            <p>¿Necesitas ayuda? Contáctanos en support@fresa.live</p>
            <p>© 2025 Fresa. Todos los derechos reservados.</p>
        </div>
    </div>
</body>
</html>
"""

    text_body = """Tu código de verificación es: {{verificationCode}}

Este código expirará en {{expirationMinutes}} minutos.

Si no solicitaste este código, por favor ignora este correo.

Gracias,
El Equipo de Fresa
"""

    ses_client = boto3.client(
        "ses", region_name=os.environ.get("AWS_REGION", "us-east-1")
    )

    try:
        response = ses_client.update_template(
            Template={
                "TemplateName": template_name,
                "SubjectPart": subject,
                "HtmlPart": html_body,
                "TextPart": text_body,
            }
        )
        print(f"✅ Template actualizado con éxito: {template_name}")
        return response
    except ses_client.exceptions.TemplateDoesNotExistException:
        print(f"📝 Template '{template_name}' no existe. Creándolo...")
        try:
            response = ses_client.create_template(
                Template={
                    "TemplateName": template_name,
                    "SubjectPart": subject,
                    "HtmlPart": html_body,
                    "TextPart": text_body,
                }
            )
            print(f"✅ Template creado con éxito: {template_name}")
            return response
        except Exception as e:
            print(f"❌ Error al crear template {template_name}: {e}")
            return None
    except Exception as e:
        print(f"❌ Error al actualizar template {template_name}: {e}")
        return None


def main():
    """Main function to create verification template"""
    print("🍓 Fresa SES Verification Template Creator")
    print("=" * 50)

    # Print AWS info
    print_aws_info()

    # Use the EXACT S3 URL format from your original script
    logo_url = "https://fresaassets.s3.us-east-1.amazonaws.com/fresaicon.png"

    # Create the verification template
    result = create_ses_template_with_logo(
        template_name="fresa-verificacion-template", logo_url=logo_url
    )

    if result:
        print("\n🎉 Verification template created/updated successfully!")
    else:
        print("\n❌ Failed to create/update verification template")


if __name__ == "__main__":
    main()
