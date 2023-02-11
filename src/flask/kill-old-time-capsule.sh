#!/bin/bash
# Delete old time capsule container
status="Killing old time capsule container"
echo $status
docker rm -f local-time-capsule