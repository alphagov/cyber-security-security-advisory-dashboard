variable "region" {
  type = "string"
  default = "eu-west-2"
}

variable "bucket_prefix" {
  type = "string"
}

variable "runtime" {
  description = "runtime for lambda"
  default     = "python3.7"
}

variable "oidc_client_id" {
  description = "OIDC client ID"
  type        = "string"
}

variable "oidc_client_secret" {
  description = "OIDC client secret"
  type        = "string"
}

variable "dns_zone_fqdn" {
  description = "The domain under which we will create our zone"
  type        = "string"
}

variable "sub_domain" {
  description = "The subdomain for our zone"
  type        = "string"
}

variable "github_org" {
  description = "GitHub organisation short-name"
  type        = "string"
}
