#! /bin/bash

docker build -t dockerenv/core docker/core
docker build -t dockerenv/postgres docker/postgres
docker build -t dockerenv/django docker/django
docker build -t dockerenv/nginx docker/nginx
