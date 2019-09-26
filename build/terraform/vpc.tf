resource "aws_vpc" "vpc" {
  cidr_block            = "10.101.0.0/16"

  enable_dns_hostnames  = false
  enable_dns_support    = true

  tags = {
    Name          = "github-audit-vpc"
    Service       = "${var.Service}"
    Environment   = "${var.Environment}"
    SvcOwner      = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL    = "${var.SvcCodeURL}"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = "${aws_vpc.vpc.id}"

  tags = {
    Name          = "github-audit-igw"
    Service       = "${var.Service}"
    Environment   = "${var.Environment}"
    SvcOwner      = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL    = "${var.SvcCodeURL}"
  }
}

module "subnet_a" {
  source                   = "modules/jump_subnet/"
  vpc_id                   = "${aws_vpc.vpc.id}"
  region                   = "${var.region}"
  igw_id                   = "${aws_internet_gateway.igw.id}"
  prefix                   = "${var.Service}-${var.Environment}"
  subnet_zone              = "${var.region}c"
  subnet_cidr_block        = "10.101.5.0/24"
}

module "subnet_b" {
  source            = "modules/public_subnet/"
  vpc_id            = "${aws_vpc.vpc.id}"
  igw_id            = "${aws_internet_gateway.igw.id}"
  nat_subnet_id     = "${module.subnet_a.public_subnet_id_out}"
  prefix            = "${var.Service}-${var.Environment}"
  subnet_zone       = "${var.region}a"
  subnet_cidr_block = "10.101.1.0/24"
}

module "subnet_c" {
  source            = "modules/public_subnet/"
  vpc_id            = "${aws_vpc.vpc.id}"
  igw_id            = "${aws_internet_gateway.igw.id}"
  nat_subnet_id     = "${module.subnet_a.public_subnet_id_out}"
  prefix            = "${var.Service}-${var.Environment}"
  subnet_zone       = "${var.region}b"
  subnet_cidr_block = "10.101.2.0/24"
}
