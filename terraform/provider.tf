terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "terraform"
  # Credentials are picked up from environment variables or `aws configure`.
  # Never hardcode access keys here or commit them to GitHub.
}
