#!/bin/bash
# Build and upload docker image
status="Building image ......"
echo $status
docker build . -t time-capsule:latest
status="Uploading image to ECR....."
echo $status
aws ecr get-login-password --region $AWS_ACCOUNT_ID_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID_TC.dkr.ecr.$AWS_ACCOUNT_ID_REGION.amazonaws.com
image_id=$(docker images --format '{{.Repository}} {{.Tag}} {{.ID}}' | grep -w "time-capsule latest" | awk '{ print $3 }')
echo $image_id
docker tag $image_id $AWS_ACCOUNT_ID_TC.dkr.ecr.$AWS_ACCOUNT_ID_REGION.amazonaws.com/time-capsule-manual:latest
docker push $AWS_ACCOUNT_ID_TC.dkr.ecr.$AWS_ACCOUNT_ID_REGION.amazonaws.com/time-capsule-manual:latest
