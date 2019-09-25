resource "aws_s3_bucket" "s3_storage" {
  bucket        = "${var.bucket_prefix}-${var.Service}-${var.Environment}-storage"
  acl           = "private"
  force_destroy = true

  tags = {
    Service       = "${var.Service}"
    Environment   = "${var.Environment}"
    SvcOwner      = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL    = "${var.SvcCodeURL}"
  }

  lifecycle_rule {
    id      = "s3-bucket-clean"
    enabled = true
    expiration {
      days = 91
    }
  }
}

data "template_file" "s3_storage_policy" {
  template = "${file("${path.module}/json/s3_storage/policy.json")}"
  vars {
    bucket_arn            = "${aws_s3_bucket.s3_storage.arn}"
    account_id            = "${data.aws_caller_identity.current.account_id}"
    audit_lambda_arn      = "${aws_iam_role.github_audit_lambda_exec_role.arn}"
    interface_lambda_arn  = "${aws_iam_role.github_interface_lambda_exec_role.arn}"
  }
}

resource "aws_s3_bucket_policy" "s3_storage_bucket_policy" {
  bucket = "${aws_s3_bucket.s3_storage.id}"
  policy = "${data.template_file.s3_storage_policy.rendered}"
}