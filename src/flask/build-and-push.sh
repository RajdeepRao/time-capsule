#!/usr/bin/env bash
# Build the Time-Capsule image and push it to ECR. Run from src/flask/.
# Requires: docker (colima ok), aws cli, git. Deploy with terraform afterwards.
set -euo pipefail

PROFILE=${AWS_PROFILE:-personal-iam}
REGION=us-east-1
REPO=time-capsule
PLATFORM=linux/arm64   # matches terraform lambda_architecture default (arm64)

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --profile "$PROFILE")
REGISTRY="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
IMAGE="$REGISTRY/$REPO"
TAG=$(git rev-parse --short HEAD)

echo ">> Logging in to ECR ($REGISTRY)"
aws ecr get-login-password --region "$REGION" --profile "$PROFILE" \
  | docker login --username AWS --password-stdin "$REGISTRY"

echo ">> Building $IMAGE:$TAG ($PLATFORM)"
docker buildx build --platform "$PLATFORM" --provenance=false \
  -t "$IMAGE:$TAG" -t "$IMAGE:latest" --load .

echo ">> Pushing"
docker push "$IMAGE:$TAG"
docker push "$IMAGE:latest"

echo ">> Pushed $IMAGE:$TAG"
echo ">> Deploy with:  (cd ../../terraform && AWS_PROFILE=$PROFILE terraform apply -var=\"image_tag=$TAG\")"
