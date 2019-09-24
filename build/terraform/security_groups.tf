# Security Groups
# SG for LB HTTPS and HTTP input and HTTPS egress to the internet
# HTTPS out is required for the LB to authenticate with Google OIDC
# -------------------

resource "aws_security_group" "alphagov_audit_alb_ingress" {
  name        = "alphagov_audit_alb_ingress"
  description = "Alphagov Audit Load Balancer SG"
  vpc_id      = "${aws_default_vpc.vpc.id}"
}

resource "aws_security_group_rule" "ingress_https_from_internet" {
  type = "ingress"

  from_port = 443
  to_port   = 443
  protocol  = "tcp"

  cidr_blocks       = ["${module.common_vars.gds_public_cidr_list}"]
  security_group_id = "${aws_security_group.alphagov_audit_alb_ingress.id}"
}

resource "aws_security_group_rule" "ingress_http_from_internet" {
  type = "ingress"

  from_port = 80
  to_port   = 80
  protocol  = "tcp"

  cidr_blocks       = ["${module.common_vars.gds_public_cidr_list}"]
  security_group_id = "${aws_security_group.alphagov_audit_alb_ingress.id}"
}


resource "aws_security_group" "alphagov_audit_alb_egress" {
  name        = "alphagov_audit_alb_ingress"
  description = "Alphagov Audit Load Balancer SG"
  vpc_id      = "${aws_default_vpc.vpc.id}"
}

resource "aws_security_group_rule" "egress_to_internet" {
  type = "egress"

  from_port = 443
  to_port   = 443
  protocol  = "tcp"

  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.alphagov_audit_alb_egress.id}"
}
