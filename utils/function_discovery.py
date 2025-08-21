#!/usr/bin/env python3
"""
Function Discovery Utility
Dynamically discovers Lambda functions from config.py and directory structure
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_functions_from_config():
    """Get function names from config.py"""
    try:
        from config import LAMBDA_FUNCTION_NAMES
        return list(LAMBDA_FUNCTION_NAMES.keys())
    except ImportError:
        return []

def get_functions_from_directory():
    """Get function names by scanning the Lambdas directory structure"""
    functions = []
    lambdas_dir = Path(__file__).parent.parent / "Lambdas"
    
    if lambdas_dir.exists():
        # Scan all category directories
        for category_dir in lambdas_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                # Scan function directories within each category
                for function_dir in category_dir.iterdir():
                    if function_dir.is_dir() and not function_dir.name.startswith('.'):
                        # Check if it has a Python file with the same name (Lambda function)
                        python_file = function_dir / f"{function_dir.name}.py"
                        if python_file.exists():
                            functions.append(function_dir.name)
    
    return sorted(list(set(functions)))

def get_all_functions():
    """Get all functions from both config and directory structure"""
    config_functions = get_functions_from_config()
    directory_functions = get_functions_from_directory()
    
    # Combine and deduplicate
    all_functions = sorted(list(set(config_functions + directory_functions)))
    return all_functions

def get_function_info(function_name):
    """Get detailed information about a specific function"""
    info = {
        "name": function_name,
        "in_config": False,
        "in_directory": False,
        "category": None,
        "path": None
    }
    
    # Check if in config
    try:
        from config import LAMBDA_FUNCTION_NAMES
        if function_name in LAMBDA_FUNCTION_NAMES:
            info["in_config"] = True
    except ImportError:
        pass
    
    # Check if in directory structure
    lambdas_dir = Path(__file__).parent.parent / "Lambdas"
    if lambdas_dir.exists():
        for category_dir in lambdas_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                function_dir = category_dir / function_name
                if function_dir.exists() and function_dir.is_dir():
                    python_file = function_dir / f"{function_name}.py"
                    if python_file.exists():
                        info["in_directory"] = True
                        info["category"] = category_dir.name
                        info["path"] = str(function_dir.relative_to(lambdas_dir.parent))
                        break
    
    return info

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python utils/function_discovery.py list")
        print("  python utils/function_discovery.py info <function_name>")
        print("  python utils/function_discovery.py config")
        print("  python utils/function_discovery.py directory")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        functions = get_all_functions()
        for func in functions:
            print(func)
    
    elif command == "config":
        functions = get_functions_from_config()
        for func in functions:
            print(func)
    
    elif command == "directory":
        functions = get_functions_from_directory()
        for func in functions:
            print(func)
    
    elif command == "info":
        if len(sys.argv) < 3:
            print("Error: Function name required")
            sys.exit(1)
        
        function_name = sys.argv[2]
        info = get_function_info(function_name)
        print(json.dumps(info, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
