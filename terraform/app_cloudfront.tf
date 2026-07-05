# Public entrypoint for the app: CloudFront -> (OAC/SigV4) -> Lambda Function URL.
# The Function URL is AWS_IAM (this account blocks anonymous URLs); OAC signs the
# origin request as the CloudFront service principal so it authenticates.

locals {
  # Function URL host (strip scheme + trailing slash) for use as the origin.
  lambda_url_host = replace(replace(aws_lambda_function_url.web.function_url, "https://", ""), "/", "")
}

resource "aws_cloudfront_origin_access_control" "app_oac" {
  name                              = "time-capsule-app-oac"
  description                       = "OAC signing for the time-capsule app Lambda function URL"
  origin_access_control_origin_type = "lambda"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# Managed policies: don't cache dynamic responses; forward everything except the
# Host header (Host must stay the origin's for SigV4 to validate).
data "aws_cloudfront_cache_policy" "caching_disabled" {
  name = "Managed-CachingDisabled"
}

data "aws_cloudfront_origin_request_policy" "all_viewer_except_host" {
  name = "Managed-AllViewerExceptHostHeader"
}

resource "aws_cloudfront_distribution" "app_dist" {
  enabled         = true
  is_ipv6_enabled = true
  comment         = "Time capsule app (Lambda function URL via OAC)"

  origin {
    domain_name              = local.lambda_url_host
    origin_id                = "lambda-app"
    origin_access_control_id = aws_cloudfront_origin_access_control.app_oac.id

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id         = "lambda-app"
    viewer_protocol_policy   = "redirect-to-https"
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    cache_policy_id          = data.aws_cloudfront_cache_policy.caching_disabled.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.all_viewer_except_host.id
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
