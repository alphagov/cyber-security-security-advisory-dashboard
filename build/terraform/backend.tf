terraform {
  backend "s3" {
    bucket  = var.state_bucket
    key     = var.state_key
    region  = var.state_region
    encrypt = var.state_encrypt
  }
}
