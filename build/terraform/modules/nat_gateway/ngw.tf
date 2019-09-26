resource "aws_nat_gateway" "ngw" {
  allocation_id = "${aws_eip.nat.id}"
  subnet_id     = "${var.subnet_id}"

  tags {
    Name = "${var.prefix}-ngw-${var.subnet_id}"
  }
}
