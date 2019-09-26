resource "aws_eip" "nat" {
  vpc = true

  tags {
    Name = "${var.prefix}-nat-eip-${var.subnet_id}"
  }
}
