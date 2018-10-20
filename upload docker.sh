#!/bin/bash

export DOCKER_ID_USER="pauapplecat"

docker login

docker build -t hupc18 .
docker tag hupc18 $DOCKER_ID_USER/hupc18
docker push $DOCKER_ID_USER/hupc18