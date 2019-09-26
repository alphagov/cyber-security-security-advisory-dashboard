# Lambda

resource "random_string" "password" {
  length = 32
  special = false
}

resource "aws_lambda_function" "github_audit_interface_lambda" {
  filename         = "../github_audit_lambda_package.zip"
  source_code_hash = "${filebase64sha256("../github_audit_lambda_package.zip")}"
  function_name    = "github_audit_interface"
  role             = "${aws_iam_role.github_interface_lambda_exec_role.arn}"
  handler          = "frontend_lambda.lambda_handler"
  runtime          = "${var.runtime}"
  timeout          = "600"

  environment {
    variables = {
      SECRET_KEY = "${random_string.password.result}"
      FLASK_ENV  = "${var.Environment}"
      GITHUB_ORG = "${var.github_org}"
    }
  }

  vpc_config {
    subnet_ids = ["${module.subnet_b.public_subnet_id_out}", "${module.subnet_c.public_subnet_id_out}"]
    security_group_ids = ["${aws_security_group.github_audit_alb_ingress.id}", "${aws_security_group.github_audit_alb_egress.id}"]
  }

  tags = {
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }
}

resource "aws_lambda_permission" "github_audit_from_alb" {
  statement_id  = "AllowExecutionFromALB"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.github_audit_interface_lambda.arn}"
  principal     = "elasticloadbalancing.amazonaws.com"
  source_arn    = "${aws_lb_target_group.github-audit-tg.arn}"
}

resource "aws_lb_target_group_attachment" "github_audit_target_group_attachment" {
  target_group_arn = "${aws_lb_target_group.github-audit-tg.arn}"
  target_id        = "${aws_lambda_function.github_audit_interface_lambda.arn}"
  depends_on       = ["aws_lambda_permission.github_audit_from_alb"]
}
