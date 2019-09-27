output "eip_id_out" {
  value = "${aws_eip.nat.id}"
}

output "eip_public_ip_out" {
  value = "${aws_eip.nat.public_ip}"
}

output "ngw_id_out" {
  value = "${aws_nat_gateway.ngw.id}"
}
