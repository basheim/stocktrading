# ML Stock Trading Service

## Summary
A basic flask service with celery jobs worker that manager the trading of an alpaca stock account. A small set of 
CRUD are also available to manage the stock, service, and jobs.

When running, this service also runs 2 redis contains for storage of models and manging the celery queue. 

TBD: Setup way to locally run without complete build script.

## Operation
The service is managed on EC2 using the shared [Release Scripts](https://github.com/basheim/release-scripts) with the 
-s identifier.

To build and push a new image, run `sh ./scripts/image_build.sh`.

To build and run a local image, run `sh ./scripts/local_build_run.sh`.