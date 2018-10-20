#!/bin/bash

export DOCKER_ID_USER="pauapplecat"

docker login

docker compose -t hupc18 .
docker docker tag hupc18 $DOCKER_ID_USER/hupc18
docker push $DOCKER_ID_USER/hupc18