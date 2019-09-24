# Lambda

resource "aws_lambda_function" "download_nvd_lambda" {
  filename         = "../cspa.zip"
  source_code_hash = "${filebase64sha256("../cspa.zip")}"
  function_name    = "cspa_download_nvd_lambda"
  role             = "${aws_iam_role.download_nvd_lambda-iam.arn}"
  handler          = "download_nvd.lambda_handler"
  runtime          = "python3.6"
  memory_size      = "3008"
  timeout          = "900"

  tags = {
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }

  environment {
    variables = {
      BUCKET_NAME = "${var.s3_bucket_name}"
      LOGLEVEL = "INFO"
    }
  }
}

resource "aws_iam_role" "download_nvd_lambda-iam" {
  name = "cspa_download_nvd_lambda_iam"

  tags = {
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }

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

resource "aws_iam_role_policy_attachment" "download_nvd_lambda-policy-attach" {
  role       = "${aws_iam_role.download_nvd_lambda-iam.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "download_nvd_lambda-iam_policy" {
  name = "download_nvd_lambda_policy"
  role = "${aws_iam_role.download_nvd_lambda-iam.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:eu-west-2:${data.aws_caller_identity.current.account_id}:*"
        },
        {
            "Effect": "Allow",
            "Action": [
              "s3:ListAllMyBuckets",
              "s3:GetBucketLocation",
              "s3:GetBucket"
            ],
            "Resource": [
              "arn:aws:s3:::*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
              "${aws_s3_bucket.s3-bucket.arn}/nvd/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:eu-west-2:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/cspa_download_nvd_lambda:*"
            ]
        }
    ]
}
EOF
}

resource "aws_cloudwatch_event_rule" "download_nvd_lambda_12_hours" {
    name = "12-hours"
    description = "Fires every 12 hours"
    schedule_expression = "cron(0 6,18 * * ? *)"
}

resource "aws_cloudwatch_event_target" "download_nvd_lambda_12_hours_tg" {
    rule = "${aws_cloudwatch_event_rule.download_nvd_lambda_12_hours.name}"
    arn = "${aws_lambda_function.download_nvd_lambda.arn}"
}

resource "aws_lambda_permission" "download_nvd_lambda_allow_cloudwatch" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.download_nvd_lambda.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.download_nvd_lambda_12_hours.arn}"
}
