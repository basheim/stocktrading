#!/bin/bash

docker build . -t basheim/stock-trader

touch .env

echo "AWS_ACCESS_KEY_ID=$(aws secretsmanager get-secret-value --secret-id ec2/linuxuser --query SecretString | jq fromjson | jq -r .key)" > .env
echo "AWS_SECRET_ACCESS_KEY=$(aws secretsmanager get-secret-value --secret-id ec2/linuxuser --query SecretString | jq fromjson | jq -r .secret_key)" >> .env
echo "AWS_DEFAULT_REGION=us-west-2" >> .env

CONTAINER_ID=$(docker ps -a --filter "name=stock-trader" -q)

if [ -n "${CONTAINER_ID}" ]; then
  docker stop "${CONTAINER_ID}"
  docker rm "${CONTAINER_ID}"
fi

docker run --env-file .env -dp 5050:5050 --name stock-trader basheim/stock-trader:latest