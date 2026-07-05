resource "aws_lambda_function" "web" {
  function_name = "time-capsule-web"
  role          = aws_iam_role.lambda_exec.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.time_capsule.repository_url}:${var.image_tag}"
  architectures = [var.lambda_architecture]
  memory_size   = 512
  timeout       = 30

  environment {
    variables = merge(
      {
        FLASK_SECRET_KEY = var.flask_secret_key
        # Wired from the TF-managed CloudFront distribution + public key so the
        # app always signs against the key CloudFront actually trusts.
        PUBLIC_KEY_ID = aws_cloudfront_public_key.cf_public_key.id
        CFD_BASE_URL  = "https://${aws_cloudfront_distribution.media_cloudfront_dist.domain_name}"
        BUCKET_NAME   = aws_s3_bucket.media_bucket.bucket
        # Large secrets (firebase admin JSON, CF private key) are NOT here — the
        # app fetches them from SSM at cold start (see config.py). Env vars must
        # stay under Lambda's 4KB total limit.
      },
      { for k, v in var.firebase_web_config : "FIREBASE_${upper(k)}" => v }
    )
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_basic]
}

# The app is fronted by an API Gateway HTTP API (see apigateway.tf), which
# invokes this function via a standard AWS_PROXY integration. No Function URL.
