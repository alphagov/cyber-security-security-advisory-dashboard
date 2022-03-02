terraform {
  backend "s3" {
    bucket  = "gds-security-terraform"
    key     = "terraform/state/account/103495720024/service/github_audit.tfstate"
    region  = "eu-west-2"
    encrypt = true
  }
}
