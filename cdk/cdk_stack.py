from aws_cdk import (
    Duration,
    Stack,
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
from pathlib import Path

# Import config from the root directory
from config import LAMBDA_FUNCTION_NAMES
from utils.aws_utils import get_aws_account_info


class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda execution role
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Create Lambda functions from source code
        recieve_email_function = _lambda.Function(
            self, "RecieveEmailFunction",
            function_name=LAMBDA_FUNCTION_NAMES["recieveEmail"],
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="recieveEmail.lambda_handler",
            code=_lambda.Code.from_asset("Lambdas/Authentication/recieveEmail"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Fresa email processing function"
        )

        signup_customer_function = _lambda.Function(
            self, "SignUpCustomerFunction",
            function_name=LAMBDA_FUNCTION_NAMES["signUpCustomer"],
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="signUpCustomer.lambda_handler",
            code=_lambda.Code.from_asset("Lambdas/Authentication/signUpCustomer"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Fresa customer signup function"
        )

        verify_code_auth_function = _lambda.Function(
            self, "VerifyCodeAndAuthHandlerFunction",
            function_name=LAMBDA_FUNCTION_NAMES["verifyCodeAndAuthHandler"],
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="verifyCodeAndAuthHandler.lambda_handler",
            code=_lambda.Code.from_asset("Lambdas/Authentication/verifyCodeAndAuthHandler"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Fresa verification function"
        )

        identity_provider_auth_function = _lambda.Function(
            self, "IdentityProviderAuthFunction",
            function_name=LAMBDA_FUNCTION_NAMES["identity_provider_auth"],
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="identity_provider_auth.lambda_handler",
            code=_lambda.Code.from_asset("Lambdas/Authentication/identity_provider_auth"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Fresa auth provider function"
        )

        # Create additional functions
        test_function = _lambda.Function(
            self, "TestFunction",
            function_name=LAMBDA_FUNCTION_NAMES["testFunction"],
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="testFunction.lambda_handler",
            code=_lambda.Code.from_asset("Lambdas/Authentication/testFunction"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Test function"
        )

        social_auth_user_function = _lambda.Function(
            self, "SocialAuthUserFunction",
            function_name=LAMBDA_FUNCTION_NAMES["social_auth_user"],
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="social_auth_user.lambda_handler",
            code=_lambda.Code.from_asset("Lambdas/Authentication/social_auth_user"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Social auth user function"
        )

        define_auth_challenge_function = _lambda.Function(
            self, "DefineAuthChallengeFunction",
            function_name=LAMBDA_FUNCTION_NAMES["defineAuthChallenge"],
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="defineAuthChallenge.lambda_handler",
            code=_lambda.Code.from_asset("Lambdas/Authentication/defineAuthChallenge"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Define auth challenge function"
        )

        verify_auth_challenge_function = _lambda.Function(
            self, "VerifyAuthChallengeFunction",
            function_name=LAMBDA_FUNCTION_NAMES["verifyAuthChallenge"],
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="verifyAuthChallenge.lambda_handler",
            code=_lambda.Code.from_asset("Lambdas/Authentication/verifyAuthChallenge"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Verify auth challenge function"
        )

        verift_auth_challenge_function = _lambda.Function(
            self, "VeriftAuthChallengeFunction",
            function_name=LAMBDA_FUNCTION_NAMES["veriftAuthChallenge"],
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="veriftAuthChallenge.lambda_handler",
            code=_lambda.Code.from_asset("Lambdas/Authentication/veriftAuthChallenge"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Verift auth challenge function"
        )

        create_auth_challenge_function = _lambda.Function(
            self, "CreateAuthChallengeFunction",
            function_name=LAMBDA_FUNCTION_NAMES["createAuthChallenge"],
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="createAuthChallenge.lambda_handler",
            code=_lambda.Code.from_asset("Lambdas/Authentication/createAuthChallenge"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            description="Create auth challenge function"
        )

        # Output the function ARNs for reference
        CfnOutput(
            self,
            "RecieveEmailArn",
            value=recieve_email_function.function_arn,
            description="ARN of the Fresa email processing Lambda function",
        )

        CfnOutput(
            self,
            "SignUpCustomerArn",
            value=signup_customer_function.function_arn,
            description="ARN of the Fresa customer signup Lambda function",
        )

        CfnOutput(
            self,
            "VerifyCodeAndAuthHandlerArn",
            value=verify_code_auth_function.function_arn,
            description="ARN of the Fresa verification Lambda function",
        )

        CfnOutput(
            self,
            "IdentityProviderAuthArn",
            value=identity_provider_auth_function.function_arn,
            description="ARN of the Fresa auth provider Lambda function",
        )

        CfnOutput(
            self,
            "TestFunctionArn",
            value=test_function.function_arn,
            description="ARN of the test Lambda function",
        )

        CfnOutput(
            self,
            "SocialAuthUserArn",
            value=social_auth_user_function.function_arn,
            description="ARN of the social auth user Lambda function",
        )

        CfnOutput(
            self,
            "DefineAuthChallengeArn",
            value=define_auth_challenge_function.function_arn,
            description="ARN of the define auth challenge Lambda function",
        )

        CfnOutput(
            self,
            "VerifyAuthChallengeArn",
            value=verify_auth_challenge_function.function_arn,
            description="ARN of the verify auth challenge Lambda function",
        )

        CfnOutput(
            self,
            "VeriftAuthChallengeArn",
            value=verift_auth_challenge_function.function_arn,
            description="ARN of the verift auth challenge Lambda function",
        )

        CfnOutput(
            self,
            "CreateAuthChallengeArn",
            value=create_auth_challenge_function.function_arn,
            description="ARN of the create auth challenge Lambda function",
        )
