variable "Service" {
  description = "Service Name"
  type        = "string"
}

variable "SvcOwner" {
  description = "Service Owner"
  type        = "string"
}

variable "Environment" {
  description = "Service Owner"
  type        = "string"
}

variable "DeployedUsing" {
  description = "Deployed Using"
  type        = "string"
  default     = "Terraform"
}

variable "SvcCodeURL" {
  description = "Service Code URL"
  type        = "string"
}
