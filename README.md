Docker ECR Cleanup Automation

1. Project Overview
This project automates cleanup of Amazon ECR Docker images using AWS Lambda.
It removes untagged (dangling) images from repositories.
It removes old images based on a retention policy.
It skips protected images such as “latest”.
It sends notifications using SNS (email) and Slack.
It runs automatically using EventBridge scheduling.
It is deployed using GitHub Actions CI/CD pipeline.


      AWS Services Used
    Service	   Purpose
AWS Lambda	    Core cleanup engine
Amazon ECR	    Docker image storage
EventBridge	    Scheduled execution
SNS	            Email notifications
Slack Webhook	Team alerts
IAM	Security    permissions
CloudWatch	     Logging

   Project Structure
docker-ecr-cleanup-automation/
│
├── lambda/
│   ├── app.py              # Lambda entry point
│   ├── ecr_cleanup.py     # Cleanup logic
│   ├── notifier.py        # SNS + Slack notifications
│
├── .github/workflows/
│   └── deploy.yml         # CI/CD pipeline
│
└── README.md

Architecture Flow
EventBridge triggers AWS Lambda on schedule
Lambda scans all ECR repositories
It fetches all images from each repository
It classifies images into:
Untagged images
Old images
Protected images
It deletes eligible images using ECR API
It sends cleanup report to:
SNS (Email notification)
Slack channel


Project Structure
lambda/app.py → Lambda entry point
lambda/ecr_cleanup.py → Core cleanup logic
lambda/notifier.py → SNS + Slack notifications
.github/workflows/deploy.yml → CI/CD pipeline
README.md → Project documentation



Workflow Execution Steps
EventBridge triggers Lambda automatically
Lambda calls describe_repositories()
It fetches images using describe_images()
It checks each image:
Untagged → mark for deletion
Old → mark for deletion
latest → skip
It deletes images using batch_delete_image()
Sends summary report to SNS + Slack


Test Scenario Setup
6.1 Create tagged image (safe image)
Build and tag image
Push to ECR as keep-tagged
6.2 Create dangling image
Push image as dangling-test
Remove tag using batch-delete-image
Image becomes untagged (dangling)



IAM Permissions Required
ecr:DescribeRepositories
ecr:DescribeImages
ecr:ListImages
ecr:BatchDeleteImage


EventBridge Schedule
Runs using cron expression
Example schedule:
Daily cleanup at 2 AM UTC  (any scheduled time as per requirement)
Cron expression:
cron(0 2 * * ? *)  


Output Example
Total Deleted Images: 3
Total Untagged Images: 1
Total Old Images: 2
Repositories Processed: 5
Status: Cleanup Completed Successfully



CI/CD Pipeline (GitHub Actions)
Code pushed to main branch
GitHub Actions triggers workflow
Lambda package is created
Deployment happens automatically to AWS Lambda
No manual deployment required
