# Reference the DNS zone for the required parent domain
data "terraform_remote_state" "dns_zone" {
  backend = "s3"
  config {
    bucket  = "cyber-security-dns-state"
    key     = "dns/${var.dns_zone_fqdn}.dns.tfstate"
    region  = "eu-west-2"
    encrypt = true
  }
}