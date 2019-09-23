variable "region" {
  type = "string"
  default = "eu-west-2"
}

variable "dns_zone_fqdn" {
  description = "The domain under which we will create our zone"
  type        = "string"
}

variable "sub_domain" {
  description = "The subdomain for our zone"
  type        = "string"
}

variable "alb_access_logs" {
  description = "S3 bucket name for ALB access logs"
  default     = "alb-access-log-firebreack-event-normalisation"
  type        = "string"
}

variable "alb_certificate_arn" {
  description = "ALB Certificate ARN address"
  default     = "arn:aws:acm:eu-west-2:489877524855:certificate/e0735739-9295-4170-aa1d-957ad499da3e"
  type        = "string"
}

variable "oidc_client_id" {
  description = "OIDC client ID"
  type        = "string"
}

variable "oidc_client_secret" {
  description = "OIDC client secret"
  type        = "string"
}

variable "runtime" {
  description = "runtime for lambda"
  default     = "python3.7"
}
