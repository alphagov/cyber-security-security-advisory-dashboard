resource "aws_lb" "github-audit-alb" {
  name               = "github-audit-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [
    "${aws_security_group.github_audit_alb_ingress.id}",
    "${aws_security_group.github_audit_alb_egress.id}"
  ]
  subnets            = [
    "${aws_default_subnet.z1.id}",
    "${aws_default_subnet.z2.id}",
    "${aws_default_subnet.z3.id}"
  ]

  access_logs {
    bucket  = "${aws_s3_bucket.s3_logs.bucket}"
    enabled = true
  }

  enable_deletion_protection = true

  tags = {
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }
}

resource "aws_lb_target_group" "github-audit-tg" {
  name        = "target-group-github-audit-alb"
  target_type = "lambda"

  health_check {
    path     = "/healthy"
    matcher  = "200"
    interval = "60"
  }
}

resource "aws_lb_listener" "github-audit-listener" {
  load_balancer_arn = "${aws_lb.github-audit-alb.arn}"
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-1-2017-01"
  certificate_arn   = "${aws_acm_certificate.github_audit_cert.arn}"

  default_action {
    target_group_arn = "${aws_lb_target_group.github-audit-tg.arn}"
    type             = "forward"
  }
}

resource "aws_lb_listener" "github-audit-listener_80" {
  load_balancer_arn = "${aws_lb.github-audit-alb.arn}"
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener_rule" "route_auth" {
  listener_arn = "${aws_lb_listener.github-audit-listener.arn}"
  priority     = 100

  action {
    type = "authenticate-oidc"

    authenticate_oidc {
      authorization_endpoint      = "https://accounts.google.com/o/oauth2/v2/auth"
      client_id                   = "${var.oidc_client_id}"
      client_secret               = "${var.oidc_client_secret}"
      issuer                      = "https://accounts.google.com"
      token_endpoint              = "https://oauth2.googleapis.com/token"
      user_info_endpoint          = "https://openidconnect.googleapis.com/v1/userinfo"
      on_unauthenticated_request  = "authenticate"
    }
  }

  action {
    target_group_arn = "${aws_lb_target_group.github-audit-tg.arn}"
    type             = "forward"
  }

  condition {
    field  = "path-pattern"
    values = ["/auth"]
  }
}
