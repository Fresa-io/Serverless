from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_events as events,
    aws_events_targets as targets,
    CfnOutput,
)
from constructs import Construct
import sys
import os

# Import config from the root directory
from config import LAMBDA_FUNCTION_NAMES

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Step 2: Reference Existing Lambda Functions (Optional Transition Phase)
        # Using Function.from_function_name() to import existing functions without recreating them
        
        # Reference existing Fresa Lambda functions by their function names from config
        recieve_email_function = _lambda.Function.from_function_name(
            self, 
            "RecieveEmailFunction",
            LAMBDA_FUNCTION_NAMES["recieveEmail"]
        )
        
        signup_customer_function = _lambda.Function.from_function_name(
            self, 
            "SignUpCustomerFunction", 
            LAMBDA_FUNCTION_NAMES["signUpCustomer"]
        )
        
        verify_code_auth_function = _lambda.Function.from_function_name(
            self, 
            "VerifyCodeAndAuthHandlerFunction", 
            LAMBDA_FUNCTION_NAMES["verifyCodeAndAuthHandler"]
        )
        
        identity_provider_auth_function = _lambda.Function.from_function_name(
            self, 
            "IdentityProviderAuthFunction", 
            LAMBDA_FUNCTION_NAMES["identity_provider_auth"]
        )
        
        # Example: Add new permissions to existing functions
        # This demonstrates how you can start managing permissions via CDK
        
        # Example 1: Grant S3 read permissions to recieveEmail
        # s3_bucket = s3.Bucket.from_bucket_name(self, "MyBucket", "my-bucket-name")
        # s3_bucket.grant_read(recieve_email_function)
        
        # Example 2: Grant SQS permissions to signup_customer
        # sqs_queue = sqs.Queue.from_queue_arn(self, "MyQueue", "arn:aws:sqs:region:account:queue-name")
        # sqs_queue.grant_consume_messages(signup_customer_function)
        
        # Example 3: Add CloudWatch Logs permissions
        recieve_email_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream", 
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )
        
        signup_customer_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )
        
        verify_code_auth_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )
        
        identity_provider_auth_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )
        
        # Example 4: Create EventBridge rule to trigger recieveEmail
        # rule = events.Rule(
        #     self, "RecieveEmailRule",
        #     schedule=events.Schedule.rate(Duration.minutes(5)),
        #     targets=[targets.LambdaFunction(recieve_email_function)]
        # )
        
        # Example 5: Create SQS queue and grant permissions to signup_customer
        # processing_queue = sqs.Queue(
        #     self, "FresaProcessingQueue",
        #     visibility_timeout=Duration.seconds(300),
        #     retention_period=Duration.days(14)
        # )
        # processing_queue.grant_consume_messages(signup_customer_function)
        
        # Output the function ARNs for reference
        CfnOutput(self, "RecieveEmailArn", 
                 value=recieve_email_function.function_arn,
                 description="ARN of the Fresa email processing Lambda function")
        
        CfnOutput(self, "SignUpCustomerArn",
                 value=signup_customer_function.function_arn, 
                 description="ARN of the Fresa customer signup Lambda function")
        
        CfnOutput(self, "VerifyCodeAndAuthHandlerArn",
                 value=verify_code_auth_function.function_arn, 
                 description="ARN of the Fresa verification Lambda function")
        
        CfnOutput(self, "IdentityProviderAuthArn",
                 value=identity_provider_auth_function.function_arn, 
                 description="ARN of the Fresa auth provider Lambda function")
