module "nat_gateway" {
  source = "../nat_gateway"
  prefix = "${var.prefix}"

  /*subnet_id = "${aws_subnet.public_subnet.id}"*/
  subnet_id = "${var.nat_subnet_id}"
}
