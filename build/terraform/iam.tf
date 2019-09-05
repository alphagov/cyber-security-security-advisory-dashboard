data "template_file" "trust" {
  template = "${file("${path.module}/json/trust.json")}"
  vars {}
}

data "template_file" "policy" {
  template = "${file("${path.module}/json/policy.json")}"
  vars {}
}

resource "aws_iam_role" "alphagov_audit_lambda_exec_role" {
  name = "alphagov_audit_lambda_exec_role"

  assume_role_policy = "${data.template_file.trust.rendered}"
}

resource "aws_iam_role_policy" "alphagov_audit_lambda_exec_role_policy" {
  name = "test_policy"
  role = "${aws_iam_role.alphagov_audit_lambda_exec_role.id}"

  policy = "${data.template_file.policy.rendered}"
}

resource "aws_iam_role_policy_attachment" "alphagov_audit_lambda_exec_role_policy_attach" {
  role       = "${aws_iam_role.alphagov_audit_lambda_exec_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

