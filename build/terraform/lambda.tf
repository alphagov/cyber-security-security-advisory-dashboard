# Lambda

resource "random_string" "password" {
  length = 32
  special = false
}

resource "aws_lambda_function" "alphagov_audit_lambda" {
  filename         = "../alphagov_audit_lambda_package.zip"
  source_code_hash = "${filebase64sha256("../alphagov_audit_lambda_package.zip")}"
  function_name    = "alphagov_audit"
  role             = "${aws_iam_role.alphagov_audit_lambda_exec_role.arn}"
  handler          = "lambda_handler.lambda_handler"
  runtime          = "${var.runtime}"

  environment {
    variables = {
      SECRET_KEY = "${random_string.password.result}"
      TEST_VAR   = "testing"
    }
  }

  # vpc_config {
  #   subnet_ids = ["${aws_subnet.alb-frontend-subnet1-AZ-A.id}", "${aws_subnet.alb-frontend-subnet2-AZ-B.id}"]
  #   security_group_ids = ["${aws_security_group.event-normalisation-lambda-ingress.id}", "${aws_security_group.event-normalisation-lambda-egress.id}"]
  # }
}

resource "aws_lambda_permission" "alphagov_audit_from_alb" {
  statement_id  = "AllowExecutionFromALB"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.alphagov_audit_lambda.arn}"
  principal     = "elasticloadbalancing.amazonaws.com"
  source_arn    = "${aws_lb_target_group.event-normalisation-tg.arn}"
}

resource "aws_lb_target_group_attachment" "alphagov_audit_target_group_attachment" {
  target_group_arn = "${aws_lb_target_group.event-normalisation-tg.arn}"
  target_id        = "${aws_lambda_function.alphagov_audit_lambda.arn}"
  depends_on       = ["aws_lambda_permission.alphagov_audit_from_alb"]
}
