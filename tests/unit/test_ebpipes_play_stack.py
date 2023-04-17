import aws_cdk as core
import aws_cdk.assertions as assertions

from ebpipes_play.ebpipes_play_stack import EbpipesPlayStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ebpipes_play/ebpipes_play_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EbpipesPlayStack(app, "ebpipes-play")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
