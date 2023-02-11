#!/bin/bash
# Build and run docker image
status="Cleaning up....."
echo $status
status="Removing exited containers....."
echo $status
docker rm $(docker ps --filter status=exited -q)
status="Removing dangling images....."
echo $status
docker rmi $(docker images --filter "dangling=true" -q --no-trunc)