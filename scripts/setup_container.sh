#!/bin/bash

rm -rf .tmp || true
mkdir .tmp
groupadd app_grp
useradd -g app_grp celery
useradd -g app_grp app
chown -R celery:app_grp .tmp
