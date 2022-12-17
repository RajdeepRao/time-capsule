terraform {
  backend "s3" {
    encrypt = true
    bucket = "time-capsule-terraform-backend"
    dynamodb_table = "terraform-state-lock-dynamodb"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}