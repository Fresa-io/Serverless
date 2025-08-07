#!/usr/bin/env python3
"""
Script to automatically add new Lambda functions to the deployment system
Usage: python add_lambda_function.py <function_name>
"""

import sys
import os
import re
from pathlib import Path

def update_config_py(function_name):
    """Update config.py with new function"""
    config_file = "config.py"
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Find the LAMBDA_FUNCTION_NAMES dictionary
    pattern = r'LAMBDA_FUNCTION_NAMES = \{([^}]+)\}'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Add new function to the dictionary
        dict_content = match.group(1)
        new_entry = f'    "{function_name}": "{function_name}",'
        
        # Check if function already exists
        if function_name not in dict_content:
            # Add before the closing brace
            updated_dict = dict_content.rstrip() + '\n' + new_entry + '\n'
            updated_content = content.replace(match.group(0), 
                                            f'LAMBDA_FUNCTION_NAMES = {{{updated_dict}}}')
            
            with open(config_file, 'w') as f:
                f.write(updated_content)
            print(f"✅ Updated {config_file}")
        else:
            print(f"⚠️  Function {function_name} already exists in {config_file}")

def update_github_workflow(function_name):
    """Update GitHub Actions workflow with new function"""
    workflow_file = ".github/workflows/deploy.yml"
    
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    # Update unit tests section
    test_pattern = r'(# Run tests for [^\n]+\n\s+cd Lambdas/Expansion/[^\n]+\n\s+python -m pytest tests/ -v[^\n]*\n\s+cd \.\./\.\./\.\.\n\s+)'
    test_match = re.search(test_pattern, content, re.DOTALL)
    
    if test_match:
        new_test = f"""          # Run tests for {function_name}
          cd Lambdas/Expansion/{function_name}
          python -m pytest tests/ -v || echo "No tests found for {function_name}"
          cd ../../..

"""
        # Add new test after existing tests
        updated_content = content.replace(test_match.group(1), 
                                        test_match.group(1) + new_test)
        
        # Update local function tests
        local_test_pattern = r'(python local_test\.py test [^\n]+\n\s+)'
        local_test_match = re.search(local_test_pattern, updated_content)
        
        if local_test_match:
            new_local_test = f"          python local_test.py test {function_name}\n"
            updated_content = updated_content.replace(local_test_match.group(1),
                                                    local_test_match.group(1) + new_local_test)
        
        # Update deployment loop
        deploy_pattern = r'for func in ([^;]+); do'
        deploy_match = re.search(deploy_pattern, updated_content)
        
        if deploy_match:
            current_funcs = deploy_match.group(1).strip()
            new_funcs = current_funcs + f" {function_name}"
            updated_content = updated_content.replace(deploy_match.group(0),
                                                    f'for func in {new_funcs}; do')
        
        with open(workflow_file, 'w') as f:
            f.write(updated_content)
        print(f"✅ Updated {workflow_file}")

def update_entrypoint_script(function_name):
    """Update entrypoint script with new function"""
    entrypoint_file = "entrypoint_enhanced.sh"
    
    with open(entrypoint_file, 'r') as f:
        content = f.read()
    
    # Find function menu section
    menu_pattern = r'(echo "📋 Available Functions:"\n\s+echo "  1\) [^"]+"\n\s+echo "  2\) [^"]+"\n\s+echo "  3\) All Functions"\n\s+echo "  4\) 🔙 Back to Main Menu")'
    menu_match = re.search(menu_pattern, content, re.DOTALL)
    
    if menu_match:
        # Count existing functions to determine new number
        function_count = len(re.findall(r'echo "  \d+\) [^"]+"', menu_match.group(1)))
        new_number = function_count + 1
        
        new_menu_entry = f'echo "  {new_number}) {function_name}"'
        updated_menu = menu_match.group(1).replace('echo "  3) All Functions"',
                                                  f'echo "  3) {function_name}"\necho "  4) All Functions"')
        updated_menu = updated_menu.replace('echo "  4) 🔙 Back to Main Menu"',
                                           'echo "  5) 🔙 Back to Main Menu"')
        
        updated_content = content.replace(menu_match.group(1), updated_menu)
        
        # Update function selection logic
        selection_pattern = r'(case \$choice in\n\s+1\) echo "[^"]+" ;;\n\s+2\) echo "[^"]+" ;;\n\s+3\) echo "all" ;;\n\s+4\) echo "back" ;;\n\s+\*) echo "invalid" ;;\n\s+esac)'
        selection_match = re.search(selection_pattern, content, re.DOTALL)
        
        if selection_match:
            new_selection = selection_match.group(1).replace('3) echo "all" ;;',
                                                            f'3) echo "{function_name}" ;;\n        4) echo "all" ;;')
            new_selection = new_selection.replace('4) echo "back" ;;',
                                                 '5) echo "back" ;;')
            updated_content = updated_content.replace(selection_match.group(1), new_selection)
        
        with open(entrypoint_file, 'w') as f:
            f.write(updated_content)
        print(f"✅ Updated {entrypoint_file}")

def create_function_structure(function_name):
    """Create the basic function directory structure"""
    base_dir = f"Lambdas/Expansion/{function_name}"
    
    # Create directories
    os.makedirs(f"{base_dir}/tests", exist_ok=True)
    os.makedirs(f"{base_dir}/test_events", exist_ok=True)
    
    # Create main function file
    main_file = f"{base_dir}/{function_name}.py"
    if not os.path.exists(main_file):
        with open(main_file, 'w') as f:
            f.write(f'''#!/usr/bin/env python3
"""
{function_name} Lambda function
"""

import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def {function_name}(event, context):
    """
    Main handler function for {function_name}
    
    Args:
        event: AWS Lambda event
        context: AWS Lambda context
        
    Returns:
        dict: Response object
    """
    try:
        logger.info(f"Processing event: {{event}}")
        
        # TODO: Add your function logic here
        
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'message': 'Function executed successfully',
                'function': '{function_name}'
            }})
        }}
        
    except Exception as e:
        logger.error(f"Error in {function_name}: {{e}}")
        return {{
            'statusCode': 500,
            'body': json.dumps({{
                'error': str(e),
                'function': '{function_name}'
            }})
        }}
''')
        print(f"✅ Created {main_file}")
    
    # Create test file
    test_file = f"{base_dir}/tests/test_{function_name}.py"
    if not os.path.exists(test_file):
        with open(test_file, 'w') as f:
            f.write(f'''#!/usr/bin/env python3
"""
Unit tests for {function_name} Lambda function
"""

import unittest
import json
import sys
import os

# Add the function directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function module
import {function_name}

class Test{function_name.replace('_', '').title()}(unittest.TestCase):
    """Test cases for {function_name} function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_event = {{
            'httpMethod': 'POST',
            'body': json.dumps({{
                'test': 'data'
            }})
        }}
        
        self.test_context = {{
            'function_name': '{function_name}',
            'function_version': '$LATEST',
            'invoked_function_arn': 'arn:aws:lambda:us-east-1:123456789012:function:{function_name}:$LATEST',
            'memory_limit_in_mb': '128',
            'aws_request_id': 'test-request-id',
            'log_group_name': '/aws/lambda/{function_name}',
            'log_stream_name': 'test-log-stream'
        }}
    
    def test_{function_name}_success(self):
        """Test successful {function_name} execution"""
        result = {function_name}.{function_name}(self.test_event, self.test_context)
        
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('message', json.loads(result['body']))
    
    def test_{function_name}_invalid_event(self):
        """Test {function_name} with invalid event"""
        invalid_event = {{}}
        result = {function_name}.{function_name}(invalid_event, self.test_context)
        
        self.assertEqual(result['statusCode'], 200)  # Should still work with empty event

if __name__ == '__main__':
    unittest.main()
''')
        print(f"✅ Created {test_file}")
    
    # Create test event
    test_event_file = f"{base_dir}/test_events/{function_name}_test_event.json"
    if not os.path.exists(test_event_file):
        with open(test_event_file, 'w') as f:
            f.write(json.dumps({
                'httpMethod': 'POST',
                'body': json.dumps({
                    'test': 'data',
                    'function': function_name
                })
            }, indent=2))
        print(f"✅ Created {test_event_file}")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python add_lambda_function.py <function_name>")
        print("Example: python add_lambda_function.py my_new_function")
        sys.exit(1)
    
    function_name = sys.argv[1]
    
    print(f"🚀 Adding new Lambda function: {function_name}")
    print("=" * 50)
    
    # Create function structure
    create_function_structure(function_name)
    
    # Update configuration files
    update_config_py(function_name)
    update_github_workflow(function_name)
    update_entrypoint_script(function_name)
    
    print("=" * 50)
    print(f"✅ Successfully added {function_name} to the deployment system!")
    print("")
    print("📋 Next steps:")
    print(f"1. Edit {function_name}.py to add your function logic")
    print(f"2. Add tests to tests/test_{function_name}.py")
    print(f"3. Create test events in test_events/")
    print("4. Test locally: docker run --rm -it app deploy <your-aws-key>")
    print("5. Push to GitHub to trigger CI/CD")

if __name__ == "__main__":
    main() 