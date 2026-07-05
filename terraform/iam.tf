data "aws_caller_identity" "current" {}

resource "aws_iam_role" "lambda_exec" {
  name = "time-capsule-lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# CloudWatch Logs for the function.
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# App permissions: media bucket access + read the two app secrets from SSM.
# NOTE: this GRANTS the Lambda access to the bucket contents; it does not modify
# the bucket, its ACL, or its public-access settings.
data "aws_iam_policy_document" "lambda_app" {
  statement {
    sid       = "MediaBucketList"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.media_bucket.arn]
  }
  statement {
    sid       = "MediaBucketObjects"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.media_bucket.arn}/*"]
  }
  statement {
    sid       = "ReadAppSecrets"
    actions   = ["ssm:GetParameter", "ssm:GetParameters"]
    resources = ["arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/time-capsule/*"]
  }
}

resource "aws_iam_role_policy" "lambda_app" {
  name   = "time-capsule-app-policy"
  role   = aws_iam_role.lambda_exec.id
  policy = data.aws_iam_policy_document.lambda_app.json
}
