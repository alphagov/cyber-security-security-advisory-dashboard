provider "aws" {
    region = "${var.region}"
}

resource "aws_lambda_function" "lambda" {
  filename         = "${var.lambda_zip_location}"
  source_code_hash = "${filebase64sha256(var.lambda_zip_location)}"
  function_name    = "${var.lambda_functionname}"
  role             = "${aws_iam_role.lambda-iam.arn}"
  handler          = "${var.lambda_handler}"
  runtime          = "${var.lambda_runtime}"
  memory_size      = "${var.lambda_memory}"
  timeout          = "${var.lambda_timeout}"


  tags             = "${map(
    "Service", "security_advisories",
    "Environment", "prod",
    "DeployedUsing", "Terraform",
  )}"

  environment {
    variables = {
      github_key: "${data.aws_kms_secrets.github_key.plaintext["github_key"]}"
    }
  }
}

resource "aws_iam_role" "lambda-iam" {
  name = "${var.lambda_functionname}_iam_role"

  tags = "${var.tags}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda-policy-attach" {
  role       = "${aws_iam_role.lambda-iam.name}"
  policy_arn = "${aws_iam_policy.lambda-iam_policy.arn}"
}

resource "aws_iam_policy" "lambda-iam_policy" {
  name = "${var.lambda_functionname}_iam_policy"

  # TODO: resource path
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "${var.lambda_logarn}:*"
        },
        {
            "Effect": "Allow",
            "Action": [
              "ssm:DescribeParameters",
              "ssm:GetParameters"
            ],
            "Resource": [
                "arn:aws:ssm:${var.region}:${var.aws_account_id}:key/alias/security-advisories-prod-kms"
            ]
        }
    ]
}
EOF
}

resource "aws_cloudwatch_event_rule" "turn_on_security_advisories_rule" {
    name = "24-hours"
    description = "Fires every 24 hours at 18:00"
    schedule_expression = "cron(0 18 * * ? *)"
}

resource "aws_cloudwatch_event_target" "turn_on_security_advisories_rule_tg" {
    rule = "${aws_cloudwatch_event_rule.turn_on_security_advisories_rule.name}"
    arn = "${aws_lambda_function.lambda.arn}"
}

resource "aws_lambda_permission" "turn_on_security_advisories_rule_allow_cloudwatch" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.lambda.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.turn_on_security_advisories_rule.arn}"
}
