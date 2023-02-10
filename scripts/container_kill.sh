#!/bin/bash

CONTAINER_ID=$(docker ps -a --filter "name=stock-trader" -q)
docker stop "${CONTAINER_ID}"
docker rm "${CONTAINER_ID}"