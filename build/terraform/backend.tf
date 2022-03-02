terraform {
  backend "s3" {
    bucket  = "gds-security-terraform"
    key     = "terraform/state/account/779799343306/service/github_audit.tfstate"
    region  = "eu-west-2"
    encrypt = true
  }
}