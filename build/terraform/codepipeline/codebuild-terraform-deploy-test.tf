module "codebuild_terraform_deploy" {
  source                      = "github.com/alphagov/cyber-security-shared-terraform-modules//codebuild/codebuild_apply_terraform"
  codebuild_service_role_name = data.aws_iam_role.pipeline_role.name
  deployment_account_id       = var.deployment_account_id
  deployment_role_name        = "CodePipelineDeployerRole_${var.deployment_account_id}"
  terraform_version           = "0.14.7"
  terraform_directory         = "build/terraform"
  codebuild_image             = var.default_container_image
  pipeline_name               = var.pipeline_name
  stage_name                  = "Deploy"
  action_name                 = "DeploySecurityAdvisoryDashboard"
  environment                 = var.environment
  docker_hub_credentials      = var.docker_hub_creds
  tags                        = local.tags
  backend_var_file            = "codepipeline/backend.tfvars"
  apply_var_file              = "codepipeline/apply.tfvars"
}