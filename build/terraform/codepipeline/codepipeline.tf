resource "aws_codepipeline" "cd-security-advisory-dashboard" {
  name     = var.pipeline_name
  role_arn = data.aws_iam_role.pipeline_role.arn
  tags     = merge(local.tags, { Name = var.pipeline_name })

  artifact_store {
    type     = "S3"
    location = data.aws_s3_bucket.artifact_store.bucket
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["git_security_advisory_dashboard"]
      configuration = {
        ConnectionArn    = "arn:aws:codestar-connections:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:connection/51c5be90-8c8f-4d32-8be4-18b8f05c802c"
        FullRepositoryId = "alphagov/cyber-security-security-advisory-dashboard"
        BranchName       = "master"
      }
    }
  }

  #stage {
    #name = "Prep"

    #action {
      #name             = "GetChangedFiles"
      #category         = "Build"
      #owner            = "AWS"
      #provider         = "CodeBuild"
      #version          = "1"
      #run_order        = 1
      #input_artifacts  = ["git_security_advisory_dashboard"]
      #output_artifacts = ["changed_files"]
      #configuration = {
        #ProjectName = module.codebuild_get_changed_file_list.project_name
      #}
    #}

    #action {
      #name             = "GetActionsRequired"
      #category         = "Build"
      #owner            = "AWS"
      #provider         = "CodeBuild"
      #version          = "1"
      #run_order        = 2
      #input_artifacts  = ["git_security_advisory_dashboard", "changed_files"]
      #output_artifacts = ["actions_required"]
      #configuration = {
        #PrimarySource = "git_security_advisory_dashboard"
        #ProjectName   = module.codebuild_get_actions_required.project_name
      #}
    #}
  #}

  stage {
    name = "SecAdvisoryTests"

    action {
      name            = "SecAdvisoryTests"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      version         = "1"
      run_order       = 1
      input_artifacts = ["git_security_advisory_dashboard"]
      configuration = {
        PrimarySource = "git_security_advisory_dashboard"
        ProjectName   = aws_codebuild_project.codebuild_build_sec_adv_tests.name
      }
    }
  }

  stage {
    name = "SecAdvisoryContractTests"

    action {
      name            = "SecAdvisoryContractTests"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      version         = "1"
      run_order       = 1
      input_artifacts = ["git_security_advisory_dashboard"]
      configuration = {
        PrimarySource = "git_security_advisory_dashboard"
        ProjectName   = aws_codebuild_project.codebuild_build_github_contract_tests.name
      }
    }
  }

  stage {
    name = "CreateLambdaDeploymentPackage"

    action {
      name            = "CreateLambdaDeploymentPackage"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      version         = "1"
      run_order       = 1
      input_artifacts = ["git_security_advisory_dashboard"]
      output_artifacts = ["git_sec_adv_dashboard_with_lambda_package"]
      configuration = {
        PrimarySource = "git_security_advisory_dashboard"
        ProjectName   = aws_codebuild_project.codebuild_build_sec_adv_pack.name
      }
    }
  }

  stage {
    name = "Deploy"
    action {
      name            = "TerraformApply"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      version         = "1"
      run_order       = 1
      input_artifacts = ["git_sec_adv_dashboard_with_lambda_package"]
      output_artifacts = [
        "staging_terraform_output"
      ]

      configuration = {
        PrimarySource = "git_sec_adv_dashboard_with_lambda_package"
        ProjectName   = module.codebuild_terraform_deploy.project_name
      }
    }
  }

  stage {
   name = "UpdatePipeline"

   action {
     name             = "UpdatePipeline"
     category         = "Build"
     owner            = "AWS"
     provider         = "CodeBuild"
     version          = "1"
     run_order        = 1
     input_artifacts  = ["git_security_advisory_dashboard"]
     output_artifacts = []

     configuration = {
       ProjectName = module.codebuild_self_update.project_name
     }
   }
  }
}