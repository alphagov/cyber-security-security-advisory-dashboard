terraform {
  required_version = "= 0.11.13"

  backend "s3" {
    bucket  = "firebreak-q1-event-normalisation"
    key     = "terraform.tfstate"
    encrypt = true
    region  = "eu-west-2"
  }
}

provider "aws" {
  region              = "eu-west-2"
  allowed_account_ids = ["489877524855"]
}

data "aws_caller_identity" "current" {}
