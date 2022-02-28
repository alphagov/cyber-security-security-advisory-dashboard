variable "region_name" {
  type    = string
  default = "eu-west-2"
}

variable "deployment_account_id" {
  description = "the account into which the terraform will be deployed"
  type        = string
  default     = "670214072732"
}

variable "deployment_role_name" {
  description = "the role used to deploy the terraform"
  type        = string
  default     = "CodePipelineDeployerRole_103495720024"
}

variable "terraform_version" {
  description = "The terraform version to be used"
  type        = string
  default     = "0.12.31"
}

variable "codebuild_service_role_name" {
  description = "the role code build uses to access other AWS services"
  type        = string
  default     = "CodePipelineExecutionRole"
}

variable "codebuild_image" {
  description = "The image that CodeBuild will use, including the tag."
  type        = string
  default     = "gdscyber/cyber-security-cd-base-image:latest"
}

variable "pipeline_name" {
  description = "The name of the pipeline this project will be a part of"
  type        = string
  default     = "security_advisory_dashboard"
}

variable "stage_name" {
  description = "The name of the pipeline stage"
  type        = string
  default     = "default"
}

variable "action_name" {
  description = "The name of the pipeline stage action"
  type        = string
  default     = "default"
}

variable "environment" {
  description = "e.g. staging, production"
  type        = string
  default     = "staging"
}

variable "docker_hub_creds" {
  description = "The name of the Secrets Manager secret that contains the username and password for the Docker Hub"
  type        = string
  default     = "docker_hub_credentials"
}

variable "tags" {
  type        = map(string)
  description = "Pass through parent service tags to CodeBuild project resource"
  default     = {}
}

variable "copy_artifacts" {
  type        = list(map(string))
  description = "A list of maps containing artifacts to import with the artifact src and destination file path"
  default     = []
}

variable "service_name" {
  description = "The name of service you are deploying"
  type        = string
  default     = "terraform_output"
}

variable "ssm_github_pat" {
  type    = string
  default = "/github/pat"
}

variable "default_container_image" {
  type    = string
  default = "gdscyber/cyber-security-cd-base-image:latest"
}

variable "ssm_deploy_key" {
  type    = string
  default = "/github/deploy-keys/cyber-security-terraform"
}