terraform {
  backend "s3" {
    encrypt = true
    bucket = "time-capsule-terraform-backend"
    dynamodb_table = "terraform-state-lock-dynamodb"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_s3_bucket" "tf_backend" {
    bucket = "time-capsule-terraform-backend"
}

resource "aws_s3_bucket_acl" "tf_backend_acl" {
  bucket = aws_s3_bucket.tf_backend.id
  acl    = "private"
}