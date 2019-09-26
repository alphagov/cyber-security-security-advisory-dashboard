output "nat_public_ip_out" {
  value = "${module.nat_gateway.eip_public_ip_out}"
}

output "nat_eip_id_out" {
  value = "${module.nat_gateway.eip_id_out}"
}

output "nat_id_out" {
  value = "${module.nat_gateway.ngw_id_out}"
}

output "public_subnet_id_out" {
  value = "${aws_subnet.public_subnet.id}"
}

output "public_route_table_id_out" {
  value = "${aws_route_table.public_route_table.id}"
}

output "public_subnet_cidr_block_out" {
  value = "${aws_subnet.public_subnet.cidr_block}"
}
