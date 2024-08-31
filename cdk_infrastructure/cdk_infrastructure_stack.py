from aws_cdk import (
    Stack,
    CfnParameter as _cfnParameter,
    aws_cognito as _cognito,
    aws_s3 as s3,
    aws_dynamodb as _dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as _apigateway,
)
from constructs import Construct
import os


class CdkInfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        bucket_name = s3.Bucket(
            self,
            "MyBucket",
            bucket_name="navaneethreddydevops-backend-api-bucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )
        user_pool = _cognito.UserPool(self, "UserPool")
        user_pool.add_client(
            "app-client",
            auth_flows=_cognito.AuthFlow(user_password=True),
            supported_identity_providers=[
                _cognito.UserPoolClientIdentityProvider.COGNITO
            ],
        )
        auth = _apigateway.CognitoUserPoolsAuthorizer(
            self, "imagesAuthorizer", cognito_user_pools=[user_pool]
        )
        my_table = _dynamodb.Table(
            self,
            id="dynamoTable",
            table_name="navaneethreddydevops-form-metadata",
            partition_key=_dynamodb.Attribute(
                name="userid", type=_dynamodb.AttributeType.STRING
            ),
        )  # change primary key here
        my_lambda = _lambda.Function(
            self,
            id="lambdafunction",
            function_name="navaneethreddydevops-formlambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_asset(os.path.join("./", "lambdas")),
            environment={
                "bucket": bucket_name.bucket_name,
                "table": my_table.table_name,
            },
        )
        bucket_name.grant_read_write(my_lambda)
        my_table.grant_read_write_data(my_lambda)
        my_api = _apigateway.LambdaRestApi(
            self,
            id="navaneethreddydeops-lambdaapi",
            rest_api_name="formapi",
            handler=my_lambda,
            proxy=True,
        )
        postData = my_api.root.add_resource("form")
        postData.add_method(
            "POST",
            authorizer=auth,
            authorization_type=_apigateway.AuthorizationType.COGNITO,
        )  # POST images/files & metadata
