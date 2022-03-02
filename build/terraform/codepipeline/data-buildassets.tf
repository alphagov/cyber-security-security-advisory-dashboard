data "aws_iam_role" "pipeline_role" {
  name = "CodePipelineExecutionRole"
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "aws_s3_bucket" "artifact_store" {
  bucket = "co-cyber-codepipeline-artifact-store"
}

data "aws_secretsmanager_secret_version" "dockerhub_creds" {
  secret_id = var.docker_hub_creds
}

data "aws_secretsmanager_secret" "dockerhub_creds" {
  name = var.docker_hub_creds
}

data "aws_ssm_parameter" "github_pat" {
  name = var.ssm_github_pat
}