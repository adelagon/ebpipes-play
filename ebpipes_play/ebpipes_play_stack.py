from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    Stack,
    SecretValue,
    aws_events as events,
    aws_iam as iam,
    aws_pipes as pipes,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_secretsmanager as sm,
)
from constructs import Construct

class EbpipesPlayStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # SQS Queue
        queue = sqs.Queue(
            self, "EbpipesPlayQueue",
            visibility_timeout=Duration.seconds(300),
        )

        queue_policy = iam.PolicyStatement(
            actions=['sqs:ReceiveMessage', 'sqs:DeleteMessage', 'sqs:GetQueueAttributes'],
            resources=[queue.queue_arn],
            effect=iam.Effect.ALLOW,
        )

        # Transform Lambda
        transform_lambda = _lambda.Function(
            self, "TransformLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="transform.handler"
        )

        # API Destination
        connection = events.Connection(self, "Connection",
            authorization=events.Authorization.api_key("x-api-key", SecretValue.secrets_manager("MockAPIKey"))
        )
        destination = events.ApiDestination(self, "Destination",
            connection=connection,
            endpoint="https://m2jlelngog.execute-api.ap-southeast-1.amazonaws.com/dev",                                    
        )
        
        # EventBridge Pipe
        pipe_role = iam.Role(self, 'PipeRole',
            assumed_by=iam.ServicePrincipal('pipes.amazonaws.com'),                     
        )

        pipe_role.add_to_policy(queue_policy)

        pipe = pipes.CfnPipe(self, "Pipe",
            role_arn=pipe_role.role_arn,
            source=queue.queue_arn,
            source_parameters=pipes.CfnPipe.PipeSourceParametersProperty(
                sqs_queue_parameters=pipes.CfnPipe.PipeSourceSqsQueueParametersProperty(
                    batch_size=5,
                    maximum_batching_window_in_seconds=60
                )
            ),
            enrichment=transform_lambda.function_arn,
            target=destination.api_destination_arn,
        )