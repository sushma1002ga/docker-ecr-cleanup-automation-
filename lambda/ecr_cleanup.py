import boto3
from datetime import datetime, timezone, timedelta

ecr = boto3.client("ecr")

DAYS_THRESHOLD = int(__import__("os").getenv("DAYS_THRESHOLD", "30"))

def get_all_repositories():
    repos = []
    paginator = ecr.get_paginator("describe_repositories")

    for page in paginator.paginate():
        for repo in page["repositories"]:
            repos.append(repo["repositoryName"])

    return repos


def cleanup_repository(repo_name):
    image_details = ecr.describe_images(repositoryName=repo_name)

    deleted = 0
    untagged = 0
    old = 0

    delete_list = []

    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_THRESHOLD)

    for img in image_details.get("imageDetails", []):

        digest = img["imageDigest"]
        pushed_at = img["imagePushedAt"]
        tags = img.get("imageTags", [])

        # skip latest protection (optional safety)
        if tags and "latest" in tags:
            continue

        # Untagged images
        if not tags:
            delete_list.append({"imageDigest": digest})
            untagged += 1
            continue

        # Old images
        if pushed_at < cutoff:
            delete_list.append({"imageDigest": digest})
            old += 1

    if delete_list:
        response = ecr.batch_delete_image(
            repositoryName=repo_name,
            imageIds=delete_list
        )
        deleted = len(response.get("imageIds", []))

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
