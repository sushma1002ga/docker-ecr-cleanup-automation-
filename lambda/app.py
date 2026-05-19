from ecr_cleanup import cleanup_all_repositories
from notifier import send_sns, send_slack

def lambda_handler(event, context):
    try:
        result = cleanup_all_repositories()

        message = f"""
🚀 ECR Cleanup Completed

Total Deleted: {result['total_deleted']}
Total Untagged: {result['total_untagged']}
Total Old: {result['total_old']}
Repositories Processed: {len(result['repositories'])}
"""

        send_sns(message)
        send_slack(message)

        return {
            "status": "success",
            "result": result
        }

    except Exception as e:
        error_msg = f"ECR Cleanup Failed: {str(e)}"
        send_sns(error_msg)
        send_slack(error_msg)
        raise
