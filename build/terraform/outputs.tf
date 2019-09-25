output "caller" {
  value = "${data.aws_caller_identity.current.account_id}"
}

output "dns" {
  value = "${aws_route53_record.csw_a_record.fqdn}"
}