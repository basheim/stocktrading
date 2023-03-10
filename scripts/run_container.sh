#!/bin/bash
mkdir -p .aws
touch ./.aws/credentials
echo "[default]" > ./.aws/credentials
echo "aws_access_key_id = $(echo $AWS_ACCESS_KEY_ID)" >> ./.aws/credentials
echo "aws_secret_access_key = $(echo $AWS_SECRET_ACCESS_KEY)" >> ./.aws/credentials
supervisord -c "supervisord.conf"