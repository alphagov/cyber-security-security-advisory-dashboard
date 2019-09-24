# Lambda

resource "random_string" "password" {
  length = 32
  special = false
}

resource "aws_lambda_function" "alphagov_audit_lambda" {
  filename         = "../alphagov_audit_lambda_package.zip"
  source_code_hash = "${filebase64sha256("../alphagov_audit_lambda_package.zip")}"
  function_name    = "github_audit_collector"
  role             = "${aws_iam_role.alphagov_audit_lambda_exec_role.arn}"
  handler          = "audit_lambda.cronable_vulnerability_audit"
  runtime          = "${var.runtime}"

  environment {
    variables = {
      SECRET_KEY = "${random_string.password.result}"
      FLASK_ENV  = "${var.Environment}"
    }
  }

  vpc_config {
    subnet_ids = ["${aws_default_subnet.z1.id}", "${aws_default_subnet.z2.id}", "${aws_default_subnet.z3.id}"]
    security_group_ids = ["${aws_security_group.alphagov_audit_alb_ingress.id}", "${aws_security_group.alphagov_audit_alb_egress.id}"]
  }

  tags = {
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }
}

resource "aws_lambda_permission" "alphagov_audit_from_alb" {
  statement_id  = "AllowExecutionFromALB"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.alphagov_audit_lambda.arn}"
  principal     = "elasticloadbalancing.amazonaws.com"
  source_arn    = "${aws_lb_target_group.github-audit-tg.arn}"
}

resource "aws_lb_target_group_attachment" "alphagov_audit_target_group_attachment" {
  target_group_arn = "${aws_lb_target_group.github-audit-tg.arn}"
  target_id        = "${aws_lambda_function.alphagov_audit_lambda.arn}"
  depends_on       = ["aws_lambda_permission.alphagov_audit_from_alb"]
}
