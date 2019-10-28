#!/bin/bash

set -e

unset AWS_SESSION_TOKEN

role_arn="$1"
region="$2"
temp_role=$(aws sts assume-role \
                    --role-arn "${role_arn}" \
                    --role-session-name "concourse-task" \
                    --duration 1800)

export AWS_ACCESS_KEY_ID=$(echo $temp_role | jq .Credentials.AccessKeyId | xargs)
export AWS_SECRET_ACCESS_KEY=$(echo $temp_role | jq .Credentials.SecretAccessKey | xargs)
export AWS_SESSION_TOKEN=$(echo $temp_role | jq .Credentials.SessionToken | xargs)
export AWS_DEFAULT_REGION=${region:-eu-west-2}
