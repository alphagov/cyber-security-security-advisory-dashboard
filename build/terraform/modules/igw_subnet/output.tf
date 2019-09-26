output "public_subnet_id_out" {
  value = "${aws_subnet.subnet.id}"
}

output "public_route_table_id_out" {
  value = "${aws_route_table.public_route_table.id}"
}
