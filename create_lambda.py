#!/usr/bin/env python3
"""
Interactive Lambda Function Creator
Usage: python3 create_lambda.py
"""

import os
import sys
import subprocess

def show_categories():
    """Show available categories"""
    print("\n📁 Available Categories:")
    print("  1) Authentication (login, signup, auth)")
    print("  2) Processing (data processing, file handling)")
    print("  3) Communication (email, SMS, notifications)")
    print("  4) Analytics (reporting, data analysis)")
    print("  5) General (default category)")
    print("  6) Custom (enter your own category)")

def get_category():
    """Get category from user"""
    show_categories()
    print("\nEnter category choice (1-6): ", end="")
    choice = input().strip()
    
    category_map = {
        "1": "Authentication",
        "2": "Processing", 
        "3": "Communication",
        "4": "Analytics",
        "5": "General"
    }
    
    if choice in category_map:
        return category_map[choice]
    elif choice == "6":
        print("Enter custom category name: ", end="")
        custom = input().strip()
        return custom if custom else "General"
    else:
        print("❌ Invalid choice. Using 'General' category.")
        return "General"

def validate_function_name(name):
    """Validate function name"""
    if not name:
        return False, "Function name cannot be empty"
    
    if not name.replace('_', '').replace('-', '').isalnum():
        return False, "Function name must contain only letters, numbers, underscores, and hyphens"
    
    # Check if function already exists
    if os.path.exists(f"Lambdas"):
        for root, dirs, files in os.walk("Lambdas"):
            if name in dirs:
                return False, f"Function '{name}' already exists in {root}"
    
    return True, "Valid"

def main():
    """Main interactive function"""
    print("🚀 Interactive Lambda Function Creator")
    print("=" * 40)
    
    # Get function name
    while True:
        print("\nEnter function name (or 'quit' to exit): ", end="")
        function_name = input().strip()
        
        if function_name.lower() == 'quit':
            print("👋 Goodbye!")
            return
        
        if not function_name:
            print("❌ Function name cannot be empty")
            continue
            
        # Validate function name
        is_valid, message = validate_function_name(function_name)
        if not is_valid:
            print(f"❌ {message}")
            continue
            
        break
    
    # Get category
    category = get_category()
    
    # Confirm creation
    print(f"\n📋 Function Details:")
    print(f"   Name: {function_name}")
    print(f"   Category: {category}")
    print(f"\nProceed with creation? (y/N): ", end="")
    confirm = input().strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("❌ Cancelled function creation")
        return
    
    # Create the function
    print(f"\n🚀 Creating Lambda function: {function_name}")
    print(f"📁 Category: {category}")
    print("=" * 50)
    
    try:
        # Run the add_lambda_function.py script
        result = subprocess.run([
            sys.executable, 
            "scripts/add_lambda_function.py", 
            function_name, 
            category
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            print("\n🎉 Successfully created Lambda function!")
            print("\n📋 Next steps:")
            print(f"1. Edit the function code: Lambdas/{category}/{function_name}/{function_name}.py")
            print("2. Add your business logic")
            print("3. Test locally using the Docker CLI")
            print("4. Push to GitHub to trigger CI/CD")
        else:
            print(f"❌ Error creating function:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running script: {e}")

if __name__ == "__main__":
    main()
