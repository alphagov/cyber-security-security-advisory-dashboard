resource "aws_s3_bucket" "s3-bucket" {
  bucket = "${var.s3_bucket_name}"
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
