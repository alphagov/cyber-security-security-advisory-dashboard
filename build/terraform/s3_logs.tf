resource "aws_s3_bucket" "s3_logs" {
  bucket        = "${var.bucket_prefix}-${var.Service}-${var.Environment}-logs"
  acl           = "log-delivery-write"
  force_destroy = true

  tags = {
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }

  lifecycle_rule {
    id      = "s3-bucket-clean"
    enabled = true
    expiration {
      days = 91
    }
  }
}

/*
data "template_file" "s3_logs_policy" {
  template = "${file("${path.module}/json/s3_logs/policy.json")}"
  vars {
    bucket_arn = "${aws_s3_bucket.s3_logs.arn}"
    account_id = "${data.aws_caller_identity.current.account_id}"
  }
}

resource "aws_s3_bucket_policy" "s3_logs_bucket_policy" {
  bucket = "${aws_s3_bucket.s3_logs.id}"
  policy = "${data.template_file.s3_logs_policy.rendered}"
}
*/

data "aws_elb_service_account" "main" {}

data "aws_iam_policy_document" "s3_logs_policy" {
    policy_id = "s3_lb_write"

    statement = {
        actions = ["s3:*"]
        resources = [
          "${aws_s3_bucket.s3_logs.arn}",
          "${aws_s3_bucket.s3_logs.arn}/*"
        ]

        principals = {
            identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/AdminRole"]
            type = "AWS"
        }
    }

    statement = {
        actions = ["s3:PutObject"]
        resources = ["${aws_s3_bucket.s3_logs.arn}/logs/*"]

        principals = {
            identifiers = ["${data.aws_elb_service_account.main.arn}"]
            type = "AWS"
        }
    }
}

resource "aws_s3_bucket_policy" "s3_logs_bucket_policy" {
  bucket = "${aws_s3_bucket.s3_logs.id}"
  policy = "${data.aws_iam_policy_document.s3_logs_policy.json}"
}