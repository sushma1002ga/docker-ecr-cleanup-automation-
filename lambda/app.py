from ecr_cleanup import cleanup_ecr_images
from notifier import send_sns, send_slack

def lambda_handler(event, context):
    try:
        result = cleanup_ecr_images()

        message = f"""
        Docker ECR Cleanup Completed:
        Deleted Images: {result['deleted']}
        Untagged: {result['untagged']}
        Old Images: {result['old']}
        """

        send_sns(message)
        send_slack(message)

        return {"status": "success", "message": message}

    except Exception as e:
        error_msg = f"ECR Cleanup Failed: {str(e)}"
        send_sns(error_msg)
        send_slack(error_msg)
        raise
