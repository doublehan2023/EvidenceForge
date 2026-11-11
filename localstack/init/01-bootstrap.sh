#!/bin/sh
set -eu

awslocal s3api head-bucket --bucket "${S3_BUCKET}" 2>/dev/null || awslocal s3api create-bucket --bucket "${S3_BUCKET}"
awslocal sqs get-queue-url --queue-name "${SQS_QUEUE_NAME}" >/dev/null 2>&1 || awslocal sqs create-queue --queue-name "${SQS_QUEUE_NAME}"
