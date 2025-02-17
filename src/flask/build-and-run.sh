#!/bin/bash
# Build and run docker image
status="Building image ....."
echo $status
docker build . -t time-capsule:latest
status="Running container on port 80....."
echo $status
docker run --name local-time-capsule -v `pwd`:/app -p 8081:8081 -d time-capsule:latest 
