import boto3
import os
import json
import urllib.request

sns = boto3.client("sns")

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
SLACK_WEBHOOK = os.environ["SLACK_WEBHOOK_URL"]


def send_sns(message):
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject="ECR Cleanup Report"
    )


def send_slack(message):
    payload = {
        "text": message
    }

    req = urllib.request.Request(
        SLACK_WEBHOOK,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    urllib.request.urlopen(req)
