variable "flask_secret_key" {
  description = "Flask session-cookie signing key"
  type        = string
  sensitive   = true
}

variable "firebase_web_config" {
  description = <<-EOT
    Pyrebase web config, snake_case keys. Each key K becomes the Lambda env var
    FIREBASE_<UPPER(K)> that config.py reads. Required keys:
    api_key, auth_domain, database_url, project_id, storage_bucket,
    messaging_sender_id, app_id, measurement_id.
  EOT
  type        = map(string)
}

variable "image_tag" {
  description = "ECR image tag to deploy to the Lambda"
  type        = string
  default     = "latest"
}

variable "lambda_architecture" {
  description = "Lambda architecture: arm64 (Graviton, cheaper) or x86_64"
  type        = string
  default     = "arm64"
}
