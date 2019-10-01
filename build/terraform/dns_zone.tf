# Reference the DNS zone for the required parent domain
data "terraform_remote_state" "dns_zone" {
  backend = "s3"
  config {
    bucket  = "${var.dns_state_bucket}"
    key     = "dns/${var.dns_zone_fqdn}.dns.tfstate"
    region  = "${var.dns_state_region}"
    encrypt = true
  }
}