#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack
from config import STACK_CONFIG, AWS_CONFIG

app = cdk.App()

# Create the stack with configuration from config.py
CdkStack(app, STACK_CONFIG["stack_name"],
    description=STACK_CONFIG["description"],
    
    # Use environment configuration from config.py
    env=cdk.Environment(
        account=AWS_CONFIG["account"] or os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=AWS_CONFIG["region"] or os.getenv('CDK_DEFAULT_REGION')
    ) if AWS_CONFIG["account"] or AWS_CONFIG["region"] else None,
)

app.synth()
