variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "bucket_prefix" {
  type = string
}

variable "runtime" {
  description = "runtime for lambda"
  default     = "python3.7"
}

variable "github_org" {
  description = "GitHub organisation short-name"
  type        = string
}

variable "aws_account_id" {
  default = "779799343306"
}

variable "lambda_zip_location" {
  default = "../github_audit_lambda_package.zip"
}

variable "dependabot_lambda_functionname" {
  default = "cyber_dependabot"
}

variable "dependabot_lambda_handler" {
  default = "cyber_dependabot.lambda_handler"
}

variable "dependabot_lambda_memory" {
  default = 1024
}

variable "dependabot_lambda_timeout" {
  default = 900
}

variable "Service" {
  description = "Service Name"
  type        = string
}

variable "SvcOwner" {
  description = "Service Owner"
  type        = string
}

variable "Environment" {
  description = "Service Owner"
  type        = string
}

variable "DeployedUsing" {
  description = "Deployed Using"
  type        = string
  default     = "Terraform"
}

variable "SvcCodeURL" {
  description = "Service Code URL"
  type        = string
}