# Keep this - hopefully we can switch to this method wth TF12
#data "terraform_remote_state" "common_vars" {
#  backend = "s3"
#  config {
#    bucket  = "cyber-security-dns-state"
#    key     = "vars/common.tfstate"
#    region  = "eu-west-2"
#    encrypt = true
#  }
#}

module "common_vars" {
  source = "git@github.com:alphagov/cyber-security-dns.git?ref=ct-770//vars/common"
}