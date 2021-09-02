#!/bin/sh

# stop all containers
docker stop $(docker ps -a -q)

#remove all exited containers
docker rm $(docker ps -a -f status=exited -q)

# remove all images having “rockiot” in name
docker image ls | grep "rockiot" | xargs docker rmi

# remove all dangling images
# docker images -f dangling=true

# clean volumes
# Docker volume prune -f
