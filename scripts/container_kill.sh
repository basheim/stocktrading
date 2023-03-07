#!/bin/bash

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
