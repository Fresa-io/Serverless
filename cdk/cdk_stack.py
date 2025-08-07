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
        
        # Reference existing Lambda functions by their function names from config
        tracer_import_results_function = _lambda.Function.from_function_name(
            self, 
            "TracerImportResultsFunction",
            LAMBDA_FUNCTION_NAMES["tracer_import_results"]
        )
        
        tracer_sqs_consumer_function = _lambda.Function.from_function_name(
            self, 
            "TracerSqsConsumerFunction", 
            LAMBDA_FUNCTION_NAMES["tracer_sqs_consumer"]
        )
        
        # Example: Add new permissions to existing functions
        # This demonstrates how you can start managing permissions via CDK
        
        # Example 1: Grant S3 read permissions to tracer_import_results
        # s3_bucket = s3.Bucket.from_bucket_name(self, "MyBucket", "my-bucket-name")
        # s3_bucket.grant_read(tracer_import_results_function)
        
        # Example 2: Grant SQS permissions to tracer_sqs_consumer
        # sqs_queue = sqs.Queue.from_queue_arn(self, "MyQueue", "arn:aws:sqs:region:account:queue-name")
        # sqs_queue.grant_consume_messages(tracer_sqs_consumer_function)
        
        # Example 3: Add CloudWatch Logs permissions
        tracer_import_results_function.add_to_role_policy(
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
        
        tracer_sqs_consumer_function.add_to_role_policy(
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
        
        # Example 4: Create EventBridge rule to trigger tracer_import_results
        # rule = events.Rule(
        #     self, "TracerImportResultsRule",
        #     schedule=events.Schedule.rate(Duration.minutes(5)),
        #     targets=[targets.LambdaFunction(tracer_import_results_function)]
        # )
        
        # Example 5: Create SQS queue and grant permissions to tracer_sqs_consumer
        # processing_queue = sqs.Queue(
        #     self, "TracerProcessingQueue",
        #     visibility_timeout=Duration.seconds(300),
        #     retention_period=Duration.days(14)
        # )
        # processing_queue.grant_consume_messages(tracer_sqs_consumer_function)
        
        # Output the function ARNs for reference
        CfnOutput(self, "TracerImportResultsArn", 
                 value=tracer_import_results_function.function_arn,
                 description="ARN of the tracer import results Lambda function")
        
        CfnOutput(self, "TracerSqsConsumerArn",
                 value=tracer_sqs_consumer_function.function_arn, 
                 description="ARN of the tracer SQS consumer Lambda function")
