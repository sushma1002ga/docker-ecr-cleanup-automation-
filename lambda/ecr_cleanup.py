import boto3
import os
from datetime import datetime, timezone, timedelta

ecr = boto3.client("ecr")

DAYS_THRESHOLD = int(os.environ.get("DAYS_THRESHOLD", "30"))


def get_all_repositories():
    repos = []
    paginator = ecr.get_paginator("describe_repositories")

    for page in paginator.paginate():
        for repo in page["repositories"]:
            repos.append(repo["repositoryName"])

    return repos


def cleanup_repository(repo_name):
    print(f"Processing repo: {repo_name}")

    response = ecr.describe_images(repositoryName=repo_name)

    image_details = response.get("imageDetails", [])

    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_THRESHOLD)

    delete_list = []
    deleted = untagged = old = 0

    for img in image_details:

        digest = img["imageDigest"]
        tags = img.get("imageTags", [])
        pushed_at = img["imagePushedAt"]

        # protect latest
        if tags and "latest" in tags:
            continue

        # untagged
        if not tags:
            delete_list.append({"imageDigest": digest})
            untagged += 1
            continue

        # old images
        if pushed_at < cutoff:
            delete_list.append({"imageDigest": digest})
            old += 1

    if delete_list:
        result = ecr.batch_delete_image(
            repositoryName=repo_name,
            imageIds=delete_list
        )
        deleted = len(result.get("imageIds", []))

    return {
        "repo": repo_name,
        "deleted": deleted,
        "untagged": untagged,
        "old": old
    }


def cleanup_all_repositories():
    repos = get_all_repositories()

    summary = []
    total_deleted = 0
    total_untagged = 0
    total_old = 0

    for repo in repos:
        result = cleanup_repository(repo)

        summary.append(result)
        total_deleted += result["deleted"]
        total_untagged += result["untagged"]
        total_old += result["old"]

    return {
        "repositories": summary,
        "total_deleted": total_deleted,
        "total_untagged": total_untagged,
        "total_old": total_old
    }
