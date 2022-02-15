resource "aws_s3_bucket" "s3_storage" {
  bucket = "${var.bucket_prefix}-${var.Service}-${var.Environment}-storage"
  
  tags = {
    Service       = var.Service
    Environment   = var.Environment
    SvcOwner      = var.SvcOwner
    DeployedUsing = var.DeployedUsing
    SvcCodeURL    = var.SvcCodeURL
  }
}

resource "aws_s3_bucket_acl" "s3_bucket_acl" {
  bucket = aws_s3_bucket.s3_storage.id
  acl    = "private"
}

resource "aws_s3_bucket_lifecycle_configuration" "bucket-config" {

  bucket = aws_s3_bucket.s3_storage.bucket

  rule {
    id = "s3-bucket-clean"

    expiration {
      days = 91
    }

    status = "Enabled"
  }
}

data "template_file" "s3_storage_policy" {
  template = file("${path.module}/json/s3_storage/policy.json")
  vars = {
    bucket_arn       = aws_s3_bucket.s3_storage.arn
    account_id       = data.aws_caller_identity.current.account_id
    audit_lambda_arn = aws_iam_role.github_audit_lambda_exec_role.arn
  }
}

resource "aws_s3_bucket_policy" "s3_storage_bucket_policy" {
  bucket = aws_s3_bucket.s3_storage.id
  policy = data.template_file.s3_storage_policy.rendered
}
