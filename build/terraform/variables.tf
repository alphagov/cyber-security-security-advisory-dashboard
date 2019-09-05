variable "vpcid" {
  description = "VPC forevent-normalisation firebreak Q1 2019"
  default     = "vpc-4dc85b25"
  type        = "string"
}

variable "aws_prim_az" {
  description = "Primary Availability Zone"
  default     = "eu-west-2a"
  type        = "string"
}

variable "aws_second_az" {
  description = "Secondary Availability Zone"
  default     = "eu-west-2b"
  type        = "string"
}

variable "cidr_subnet1_allocation" {
  description = "Subnet IP CIDR range AZ A"
  default     = "172.31.128.0/24"
  type        = "string"
}

variable "cidr_subnet2_allocation" {
  description = "Subnet IP CIDR range AZ B"
  default     = "172.31.144.0/24"
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
