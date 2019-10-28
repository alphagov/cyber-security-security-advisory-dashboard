variable "region" {
  default  = "eu-west-2"
}

variable "aws_account_id" {
  default  = "779799343306"
}

# TODO
variable "lambda_zip_location" { 
  default = "function.zip"
}

variable "lambda_functionname" { 
  default = "cyber_dependabot"
}

variable "lambda_existingrole" {
  default = ""
}

variable "lambda_timeout" {
  default  = 900
}
variable "lambda_memory" {
  default  = 128
}
variable "lambda_runtime" {
  default  = "python3.7"
}

variable "lambda_handler" {
  default  = "enable_vulnerability_alerts"
}
variable "lambda_logarn" {
  default  = "arn:aws:logs:eu-west-2:*"
}

variable "lambda_envvars" {
  type = "map"
  default = {}
}

variable "tags" {
  type = "map"
  default = {}
}
