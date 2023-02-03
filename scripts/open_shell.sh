#!/bin/bash

CONTAINER_ID=$(docker ps -a --filter "name=stock-trader" -q)
docker exec -it "${CONTAINER_ID}" sh