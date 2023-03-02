#!/bin/bash
touch .env

echo "AWS_ACCESS_KEY_ID=$(aws secretsmanager get-secret-value --secret-id ec2/linuxuser --query SecretString | jq fromjson | jq -r .key)" > .env
echo "AWS_SECRET_ACCESS_KEY=$(aws secretsmanager get-secret-value --secret-id ec2/linuxuser --query SecretString | jq fromjson | jq -r .secret_key)" >> .env
echo "AWS_DEFAULT_REGION=us-west-2" >> .env

CONTAINER_ID_TRADER=$(docker ps -a --filter "name=stock-trader" -q)
CONTAINER_ID_REDIS_QUEUE=$(docker ps -a --filter "name=redis-queue" -q)
CONTAINER_ID_REDIS_MODELS=$(docker ps -a --filter "name=redis-models" -q)
NETWORK=$(docker network ls --filter "name=stock-network" -q)

if [ -n "${CONTAINER_ID_TRADER}" ]; then
  docker stop "${CONTAINER_ID_TRADER}"
  docker rm "${CONTAINER_ID_TRADER}"
fi

if [ -n "${CONTAINER_ID_REDIS_QUEUE}" ]; then
  docker stop "${CONTAINER_ID_REDIS_QUEUE}"
  docker rm "${CONTAINER_ID_REDIS_QUEUE}"
fi

if [ -n "${CONTAINER_ID_REDIS_MODELS}" ]; then
  docker stop "${CONTAINER_ID_REDIS_MODELS}"
  docker rm "${CONTAINER_ID_REDIS_MODELS}"
fi

if [ -n "${NETWORK}" ]; then
  docker network rm "${NETWORK}"
fi

docker pull basheim/stock-trader:latest
docker pull redis

docker network create stock-network
docker run -d --name redis-queue --net stock-network -p 6381:6379 redis
docker run -d --name redis-models --net stock-network -p 6380:6379 redis
docker run --env-file .env -d -p 5050:5050 --name stock-trader --net stock-network basheim/stock-trader:latest