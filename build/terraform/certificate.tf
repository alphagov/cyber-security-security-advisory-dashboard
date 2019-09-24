resource "aws_acm_certificate" "github_audit_cert" {
  provider          = "aws.use1"
  domain_name       = "${var.sub_domain}.${var.dns_zone_fqdn}"
  validation_method = "DNS"

  tags = {
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "cert_validation_record" {
  depends_on  = ["aws_acm_certificate.github_audit_cert"]
  zone_id     = "${data.terraform_remote_state.dns_zone.zone_id}"
  name        = "${lookup(aws_acm_certificate.github_audit_cert.domain_validation_options[0], "resource_record_name")}"
  type        = "${lookup(aws_acm_certificate.github_audit_cert.domain_validation_options[0], "resource_record_type")}"
  ttl         = "86400"

  records = [
    "${lookup(aws_acm_certificate.github_audit_cert.domain_validation_options[0], "resource_record_value")}"
  ]
}

