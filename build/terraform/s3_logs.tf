resource "aws_s3_bucket" "s3_logs" {
  bucket = "${var.bucket_prefix}-${var.Service}-${var.Environment}-logs"
  acl    = "private"

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
