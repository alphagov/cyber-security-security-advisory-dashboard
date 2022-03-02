module "codebuild_get_changed_file_list" {
  source                      = "github.com/alphagov/cyber-security-shared-terraform-modules//codebuild/codebuild_get_changed_file_list"
  codebuild_service_role_name = data.aws_iam_role.pipeline_role.name
  deployment_account_id       = data.aws_caller_identity.current.account_id
  deployment_role_name        = "CodePipelineDeployerRole_${data.aws_caller_identity.current.account_id}"
  codebuild_image             = var.default_container_image
  pipeline_name               = var.pipeline_name
  environment                 = var.environment
  github_pat                  = var.ssm_github_pat
  stage_name                  = "Changes"
  action_name                 = "GetChangedFiles"
  repo_name                   = "centralised-security-logging-service"
  docker_hub_credentials      = var.docker_hub_creds
  output_artifact_path        = "changed_files.json"
}