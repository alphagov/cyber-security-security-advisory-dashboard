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

variable "github_org" {
  description = "GitHub organisation short-name"
  type        = "string"
}
