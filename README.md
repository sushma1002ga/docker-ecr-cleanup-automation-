# Docker ECR Cleanup Automation

Automated solution for managing Amazon ECR (Elastic Container Registry) Docker images using AWS Lambda. This project intelligently removes untagged and outdated images while protecting critical releases.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [AWS Services](#aws-services)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup & Configuration](#setup--configuration)
- [Workflow Execution](#workflow-execution)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)

## Overview

This project automates cleanup of Amazon ECR Docker images using AWS Lambda, implementing intelligent retention policies while ensuring critical images remain protected.

## Features

✓ **Automated cleanup** - Remove untagged (dangling) images from repositories  
✓ **Retention policy** - Delete old images based on configurable policies  
✓ **Protected images** - Skip critical tags like "latest"  
✓ **Notifications** - Multi-channel alerts via SNS (email) and Slack  
✓ **Scheduled execution** - Automatic runs using EventBridge scheduling  
✓ **CI/CD ready** - GitHub Actions deployment pipeline  

## AWS Services

| Service | Purpose |
|---------|---------|
| AWS Lambda | Core cleanup engine |
| Amazon ECR | Docker image storage |
| EventBridge | Scheduled execution triggers |
| SNS | Email notifications |
| Slack Webhook | Team alerts |
| IAM | Security permissions |
| CloudWatch | Logging & monitoring |

## Project Structure

```
docker-ecr-cleanup-automation/
│
├── lambda/
│   ├── app.py                 # Lambda entry point
│   ├── ecr_cleanup.py         # Core cleanup logic
│   └── notifier.py            # SNS + Slack notifications
│
├── .github/workflows/
│   └── deploy.yml             # CI/CD pipeline
│
└── README.md                  # Project documentation
```

## Architecture

The solution follows this execution flow:

1. **Trigger** - EventBridge invokes AWS Lambda on schedule
2. **Scan** - Lambda scans all ECR repositories
3. **Classify** - Images categorized as:
   - Untagged images (candidates for deletion)
   - Old images (based on retention policy)
   - Protected images (skip deletion)
4. **Delete** - Eligible images removed using ECR API
5. **Notify** - Cleanup report sent to:
   - SNS (Email notification)
   - Slack channel

## Prerequisites

- AWS Account with ECR repositories
- Lambda execution role with appropriate IAM permissions
- SNS topic for email notifications
- Slack webhook URL (optional)
- GitHub repository for CI/CD

## Setup & Configuration

### Required IAM Permissions

The Lambda execution role must include:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:DescribeRepositories",
        "ecr:DescribeImages",
        "ecr:ListImages",
        "ecr:BatchDeleteImage"
      ],
      "Resource": "*"
    }
  ]
}
```

### EventBridge Schedule

Configure the cleanup schedule using a cron expression:

```
cron(0 2 * * ? *)    # Daily cleanup at 2 AM UTC
```

Modify the time based on your requirements.

## Workflow Execution

The Lambda function executes the following steps:

1. Call `describe_repositories()` to list all ECR repositories
2. Fetch images using `describe_images()` for each repository
3. Evaluate each image:
   - **Untagged** → Mark for deletion
   - **Old** → Mark for deletion (based on age threshold)
   - **Protected** (e.g., "latest") → Skip
4. Delete eligible images using `batch_delete_image()`
5. Send cleanup summary report to SNS and Slack

## Testing

### Test Scenario: Tagged Image (Protected)

1. Build and tag image locally
2. Push to ECR with tag: `keep-tagged`
3. Verify image is preserved after cleanup

### Test Scenario: Dangling Image (Untagged)

1. Push image with tag: `dangling-test`
2. Remove tag using `batch_delete_image()`
3. Image becomes untagged
4. Verify image is deleted after cleanup

### Sample Output

```
Total Deleted Images:     3
Total Untagged Images:    1
Total Old Images:         2
Repositories Processed:   5
Status:                   Cleanup Completed Successfully
```

## CI/CD Pipeline

This project uses **GitHub Actions** for automated deployment:

1. Code pushed to `main` branch
2. GitHub Actions workflow triggers automatically
3. Lambda package created
4. Automatic deployment to AWS Lambda
5. No manual deployment required

### Workflow File: `.github/workflows/deploy.yml`

The deployment pipeline:
- Builds the Lambda package
- Deploys to AWS Lambda
- Validates the deployment
- Sends status notifications

---

**Maintainer:** [Your Name]  
**License:** MIT  
**Last Updated:** 2026-05-19
