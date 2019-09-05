# ALB Frontend Subnet 1 AZ A
resource "aws_subnet" "alb-frontend-subnet1-AZ-A" {
  availability_zone       = "${var.aws_prim_az}"
  cidr_block              = "${var.cidr_subnet1_allocation}"
  map_public_ip_on_launch = false
  vpc_id                  = "${var.vpcid}"

  tags {
    Name      = "firebreak-q1-event-normalisation-subnet-2-az-a"
    Product   = "subnet"
    ManagedBy = "terraform"
  }
}

# ALB Frontend Subnet 2 AZ B
resource "aws_subnet" "alb-frontend-subnet2-AZ-B" {
  availability_zone       = "${var.aws_second_az}"
  cidr_block              = "${var.cidr_subnet2_allocation}"
  map_public_ip_on_launch = false
  vpc_id                  = "${var.vpcid}"

  tags {
    Name      = "firebreak-q1-event-normalisation-subnet-2-az-b"
    Product   = "subnet"
    ManagedBy = "terraform"
  }
}

# An ingress security group for the event-normalisation ALB
resource "aws_security_group" "event-normalisation-alb-ingress" {
  vpc_id      = "${var.vpcid}"
  name        = "event-normalisation-alb-ingress"
  description = "An ingress security group for the event-normalisation ALB."

  # HTTPS in from everywhere
  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP in from everywhere
  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name      = "event-normalisation-alb-sg-ingress"
    Product   = "security-group"
    ManagedBy = "terraform"
  }
}

# An egress security group for the event-normalisation ALB
resource "aws_security_group" "event-normalisation-alb-egress" {
  vpc_id      = "${var.vpcid}"
  name        = "event-normalisation-alb-egress"
  description = "An egress security group for the event-normalisation ALB."

  # HTTPS egress to the internal VPC range
  egress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["${var.cidr_subnet1_allocation}", "${var.cidr_subnet2_allocation}"]
  }

  tags {
    Name      = "event-normalisation-alb-sg-egress"
    Product   = "security-group"
    ManagedBy = "terraform"
  }
}

# A security group for the event-normalisation lambda ingress
resource "aws_security_group" "event-normalisation-lambda-ingress" {
  vpc_id      = "${var.vpcid}"
  name        = "event-normalisation-lambda-ingress"
  description = "A security group for the event-normalisation Lambda ingress"

  # HTTPS ingress to the lambda from the ALB 
  egress {
    protocol        = "tcp"
    from_port       = 443
    to_port         = 443
    security_groups = ["${aws_security_group.event-normalisation-alb-egress.id}"]
  }

  tags {
    Name      = "event-normalisation-lambda-sg-ingress"
    Product   = "security-group"
    ManagedBy = "terraform"
  }
}

# A security group for the event-normalisation lambda egress
resource "aws_security_group" "event-normalisation-lambda-egress" {
  vpc_id      = "${var.vpcid}"
  name        = "event-normalisation-lambda-egress"
  description = "A security group for the event-normalisation Lambda egress"

  # egress from the lambda 
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name      = "event-normalisation-lambda-sg-egress"
    Product   = "security-group"
    ManagedBy = "terraform"
  }
}

## An internet gateway for the VPC
#resource "aws_internet_gateway" "main-igw" {
#  vpc_id = "${var.vpcid}"
#
#  tags {
#    Name          = "firebreak-q1-event-normalisation"
#    Product       = "internet-gateway"
#    ManagedBy     = "terraform"
#  }
#}
#
## Main Route table
#resource "aws_route_table" "main-route-table" {
#  vpc_id = "${var.vpcid}"
#
#  tags {
#    Name          = "firebreak-q1-event-normalisation"
#    Product       = "route-table"
#    ManagedBy     = "terraform"
#  }
#
## A default route via the internet gateway
#  route {
#    cidr_block = "0.0.0.0/0"
#    gateway_id = "${aws_internet_gateway.main-igw.id}"
#  }
#}
#
## Associate main route table with frontend subnet
#resource "aws_route_table_association" "main-rt-table-assoc" {
#  subnet_id      = "${aws_subnet.alb-frontend-subnet.id}"
#  route_table_id = "${aws_route_table.main-route-table.id}"
#}

