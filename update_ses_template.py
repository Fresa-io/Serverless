#!/usr/bin/env python3
"""
Custom SES Template Updater
Easy script to update your SES templates with custom content
"""

import sys
import os
from pathlib import Path

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))

from services.ses.template_manager import SESTemplateManager


def update_verification_template():
    """Update the verification template with new content"""
    manager = SESTemplateManager()

    # Your custom template content
    new_subject = "🍓 Fresa: Verificación de Email"

    new_html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Verificación de Email - Fresa</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .content { background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .button { background-color: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }
            .footer { text-align: center; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="color: #2c3e50;">🍓 Fresa</h1>
        </div>
        
        <div class="content">
            <h2 style="color: #2c3e50; margin-top: 0;">Verificación de Email</h2>
            <p>Hola,</p>
            <p>Para completar tu registro en Fresa, por favor verifica tu dirección de email haciendo clic en el siguiente enlace:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{verification_link}}" class="button">
                    Verificar Email
                </a>
            </div>
            
            <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
            <p style="word-break: break-all; color: #666;">{{verification_link}}</p>
            
            <p>Este enlace expirará en 24 horas.</p>
        </div>
        
        <div class="footer">
            <p>Si no solicitaste este email, puedes ignorarlo de forma segura.</p>
            <p>© 2025 Fresa. Todos los derechos reservados.</p>
        </div>
    </body>
    </html>
    """

    new_text_content = """
    Verificación de Email - Fresa
    
    Hola,
    
    Para completar tu registro en Fresa, por favor verifica tu dirección de email visitando el siguiente enlace:
    
    {{verification_link}}
    
    Este enlace expirará en 24 horas.
    
    Si no solicitaste este email, puedes ignorarlo de forma segura.
    
    © 2025 Fresa. Todos los derechos reservados.
    """

    # Update the template
    success = manager.update_template(
        "fresa-verificacion-template", new_subject, new_html_content, new_text_content
    )

    if success:
        print("✅ Verification template updated successfully!")
    else:
        print("❌ Failed to update verification template")

    return success


def update_welcome_template():
    """Update the welcome template with new content"""
    manager = SESTemplateManager()

    # Your custom welcome template content
    new_subject = "🍓 ¡Bienvenido a Fresa!"

    new_html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Bienvenido a Fresa</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .content { background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .button { background-color: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }
            .footer { text-align: center; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="color: #2c3e50;">🍓 Fresa</h1>
        </div>
        
        <div class="content">
            <h2 style="color: #2c3e50; margin-top: 0;">¡Bienvenido a Fresa!</h2>
            <p>Hola {{user_name}},</p>
            <p>¡Gracias por unirte a Fresa! Estamos emocionados de tenerte en nuestra comunidad.</p>
            
            <p>Con Fresa podrás:</p>
            <ul>
                <li>Gestionar tu cuenta de forma segura</li>
                <li>Acceder a todas nuestras funcionalidades</li>
                <li>Recibir actualizaciones importantes</li>
            </ul>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{dashboard_link}}" class="button">
                    Ir a mi Dashboard
                </a>
            </div>
            
            <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
        </div>
        
        <div class="footer">
            <p>¡Gracias por elegir Fresa!</p>
            <p>© 2025 Fresa. Todos los derechos reservados.</p>
        </div>
    </body>
    </html>
    """

    new_text_content = """
    ¡Bienvenido a Fresa!
    
    Hola {{user_name}},
    
    ¡Gracias por unirte a Fresa! Estamos emocionados de tenerte en nuestra comunidad.
    
    Con Fresa podrás:
    - Gestionar tu cuenta de forma segura
    - Acceder a todas nuestras funcionalidades
    - Recibir actualizaciones importantes
    
    Ir a mi Dashboard: {{dashboard_link}}
    
    Si tienes alguna pregunta, no dudes en contactarnos.
    
    ¡Gracias por elegir Fresa!
    © 2025 Fresa. Todos los derechos reservados.
    """

    # Update the template
    success = manager.update_template(
        "fresa-welcome-template", new_subject, new_html_content, new_text_content
    )

    if success:
        print("✅ Welcome template updated successfully!")
    else:
        print("❌ Failed to update welcome template")

    return success


def main():
    """Main function to update templates"""
    print("🍓 Fresa SES Template Updater")
    print("=" * 40)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python update_ses_template.py verification")
        print("  python update_ses_template.py welcome")
        print("  python update_ses_template.py all")
        sys.exit(1)

    command = sys.argv[1]

    if command == "verification":
        update_verification_template()
    elif command == "welcome":
        update_welcome_template()
    elif command == "all":
        print("Updating all templates...")
        update_verification_template()
        update_welcome_template()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()