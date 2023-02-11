#!/bin/bash
# Build and run docker image
status="Building image ....."
echo $status
docker build . -t time-capsule:latest
status="Running container on port 5000....."
echo $status
docker run --name local-time-capsule -v `pwd`:/app -p 5000:5000 -d time-capsule:latest 