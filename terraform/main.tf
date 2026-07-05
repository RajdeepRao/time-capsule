terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.51" # >= 5.51 for CloudFront OAC with lambda origin type
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = "us-east-1"
  profile = "personal-iam"
}