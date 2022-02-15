data "template_file" "dependabot_lambda_policy" {
  template = file("${path.module}/json/dependabot_lambda/policy.json")
  vars = {
    region         = var.region
    aws_account_id = var.aws_account_id
  }
}

data "template_file" "dependabot_lambda_trust" {
  template = file("${path.module}/json/dependabot_lambda/trust.json")
  vars     = {}
}

resource "aws_iam_role" "github_dependabot_lambda_exec_role" {
  name               = "github_dependabot_lambda_exec_role"
  assume_role_policy = data.template_file.dependabot_lambda_trust.rendered

  tags = map(
    "Service", "security_advisories",
    "Environment", "prod",
    "DeployedUsing", "Terraform",
  )
}

resource "aws_iam_role_policy" "github_dependabot_lambda_exec_role_policy" {
  name   = "github_dependabot_lambda_exec_role_policy"
  role   = aws_iam_role.github_dependabot_lambda_exec_role.id
  policy = data.template_file.dependabot_lambda_policy.rendered
}
