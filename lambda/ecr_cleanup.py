import boto3
from datetime import datetime, timezone, timedelta

ecr = boto3.client("ecr")

# CONFIG
REPO_NAME = "your-ecr-repo"
DAYS_THRESHOLD = 30


def cleanup_ecr_images():
    images = ecr.list_images(repositoryName=REPO_NAME)

    image_details = ecr.describe_images(repositoryName=REPO_NAME)

    deleted = 0
    untagged = 0
    old = 0

    delete_list = []

    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_THRESHOLD)

    for img in image_details["imageDetails"]:

        image_digest = img["imageDigest"]
        pushed_at = img["imagePushedAt"]
        tags = img.get("imageTags", [])

        # 1. Untagged images
        if not tags:
            delete_list.append({"imageDigest": image_digest})
            untagged += 1
            continue

        # 2. Old images
        if pushed_at < cutoff:
            delete_list.append({"imageDigest": image_digest})
            old += 1

    # Delete images in batch
    if delete_list:
        response = ecr.batch_delete_image(
            repositoryName=REPO_NAME,
            imageIds=delete_list
        )
        deleted = len(response.get("imageIds", []))

    return {
        "deleted": deleted,
        "untagged": untagged,
        "old": old
    }
