# Create an aliased A record pointing to the cloud front distribution endpoint
resource "aws_route53_record" "csw_a_record" {
  zone_id = "${data.terraform_remote_state.dns_zone.zone_id}"
  name    = "${var.sub_domain}"
  type    = "A"

  alias {
    name                   = "${aws_lb.event-normalisation-alb.dns_name}"
    zone_id                = "${aws_lb.event-normalisation-alb.zone_id}"
    evaluate_target_health = true
  }
}
