import boto3
import os
from datetime import datetime, timezone, timedelta

ecr = boto3.client("ecr")

DAYS_THRESHOLD = int(os.environ.get("DAYS_THRESHOLD", "30"))


# ----------------------------
# Get all repositories
# ----------------------------
def get_all_repositories():
    repos = []
    paginator = ecr.get_paginator("describe_repositories")

    for page in paginator.paginate():
        for repo in page.get("repositories", []):
            repos.append(repo["repositoryName"])

    return repos


# ----------------------------
# Cleanup single repository
# ----------------------------
def cleanup_repository(repo_name):
    print(f"\nProcessing repo: {repo_name}")

    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_THRESHOLD)

    image_details = []

    # ✅ FIX 1: Pagination added
    paginator = ecr.get_paginator("describe_images")

    for page in paginator.paginate(repositoryName=repo_name):
        image_details.extend(page.get("imageDetails", []))

    delete_list = []
    deleted = 0
    untagged = 0
    old = 0

    for img in image_details:

        digest = img["imageDigest"]
        tags = img.get("imageTags") or []
        pushed_at = img["imagePushedAt"]

        # Skip latest (safety)
        if "latest" in tags:
            continue

        # ----------------------------
        # Untagged images
        # ----------------------------
        if len(tags) == 0:
            delete_list.append({"imageDigest": digest})
            untagged += 1
            continue

        # ----------------------------
        # Old images
        # ----------------------------
        if pushed_at < cutoff:
            delete_list.append({"imageDigest": digest})
            old += 1

    # ----------------------------
    # Delete images
    # ----------------------------
    if delete_list:
        print(f"Deleting {len(delete_list)} images from {repo_name}")

        response = ecr.batch_delete_image(
            repositoryName=repo_name,
            imageIds=delete_list
        )

        # ✅ FIX 2: handle failures properly
        print("DELETE RESPONSE:", response)

        failures = response.get("failures", [])
        success = response.get("imageIds", [])

        if failures:
            print("DELETE FAILURES:", failures)

        deleted = len(success)

    return {
        "repo": repo_name,
        "deleted": deleted,
        "untagged": untagged,
        "old": old
    }


# ----------------------------
# Cleanup all repositories
# ----------------------------
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
