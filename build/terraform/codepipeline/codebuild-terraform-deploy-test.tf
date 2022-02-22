module "codebuild_terraform_deploy_staging" {
  source                      = "github.com/alphagov/cyber-security-shared-terraform-modules//codebuild/codebuild_apply_terraform"
  codebuild_service_role_name = data.aws_iam_role.pipeline_role.name
  deployment_account_id       = var.test_account_id
  deployment_role_name        = "CodePipelineDeployerRole_${var.test_account_id}"
  terraform_version           = "0.14.7"
  terraform_directory         = "terraform/codepipeline"
  codebuild_image             = var.default_container_image
  pipeline_name               = var.pipeline_name
  stage_name                  = "DeployStaging"
  action_name                 = "DeploySecurityAdvisoryDashboardStaging"
  environment                 = var.environment
  docker_hub_credentials      = var.docker_hub_creds
  tags                        = local.tags
  copy_artifacts              = [
    {
      artifact = "ssh_config",
      source   = ".ssh"
      target   = "/root/.ssh"
    }
  ]
}