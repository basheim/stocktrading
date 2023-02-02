#!/bin/bash

CONTAINER_ID=$(docker ps -a --filter "name=stock-trader" -q)
docker logs "${CONTAINER_ID}" | grep -v "/py/api/health" | less