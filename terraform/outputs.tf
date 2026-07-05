output "ecr_repository_url" {
  description = "Push images here"
  value       = aws_ecr_repository.time_capsule.repository_url
}

output "function_url" {
  description = "Public HTTPS URL of the app"
  value       = aws_lambda_function_url.web.function_url
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain used for signed media URLs"
  value       = aws_cloudfront_distribution.media_cloudfront_dist.domain_name
}

output "cf_public_key_id" {
  description = "CloudFront public key id the app signs with"
  value       = aws_cloudfront_public_key.cf_public_key.id
}
