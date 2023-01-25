#!/bin/bash
mkdir -p .aws
touch ./.aws/credentials
echo "[default]" > ./.aws/credentials
echo "aws_access_key_id = $(aws secretsmanager get-secret-value --secret-id ec2/linuxuser --query SecretString | jq fromjson | jq -r .key)" >> ./.aws/credentials
echo "aws_secret_access_key = $(aws secretsmanager get-secret-value --secret-id ec2/linuxuser --query SecretString | jq fromjson | jq -r .secret_key)" >> ./.aws/credentials
pip install -r requirements.txt
gunicorn -w 4 -b 127.0.0.1:5050 'app:app'