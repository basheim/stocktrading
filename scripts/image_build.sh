#!/bin/bash

docker build . -t basheim/stock-trader
docker push basheim/stock-trader:latest
