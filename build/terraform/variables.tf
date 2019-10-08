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

variable "state_bucket" {
  description = "The state bucket"
  type        = "string"
}

variable "stats_key" {
  description = "The state bucket filename"
  type        = "string"
}

variable "state_region" {
  description = "The region that the state_bucket is in"
  type        = "string"
}

variable "state_encrypt" {
  description = "Is the state_bucket encrypted?"
  type        = "string"
}
