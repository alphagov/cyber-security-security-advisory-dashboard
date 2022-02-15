resource "aws_lambda_function" "lambda" {
  filename         = var.lambda_zip_location
  source_code_hash = filebase64sha256(var.lambda_zip_location)
  function_name    = var.dependabot_lambda_functionname
  role             = aws_iam_role.github_dependabot_lambda_exec_role.arn
  handler          = var.dependabot_lambda_handler
  runtime          = var.runtime
  memory_size      = var.dependabot_lambda_memory
  timeout          = var.dependabot_lambda_timeout


  tags = map(
    "Service", "security_advisories",
    "Environment", "prod",
    "DeployedUsing", "Terraform",
  )

  environment {
    variables = {
      FLASK_ENV = "production"
    }
  }
}

resource "aws_cloudwatch_event_rule" "turn_on_security_advisories_rule" {
  name                = "24-hours"
  description         = "Fires every 24 hours at 23:30"
  schedule_expression = "cron(30 23 * * ? *)"
}

resource "aws_cloudwatch_event_target" "turn_on_security_advisories_rule_tg" {
  rule = aws_cloudwatch_event_rule.turn_on_security_advisories_rule.name
  arn  = aws_lambda_function.lambda.arn
}

resource "aws_lambda_permission" "turn_on_security_advisories_rule_allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.turn_on_security_advisories_rule.arn
}
