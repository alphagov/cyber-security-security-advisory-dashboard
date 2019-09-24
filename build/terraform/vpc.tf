resource "aws_default_vpc" "vpc" {
  tags = {
    Name = "github-audit-prod-vpc"
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }
}

resource "aws_default_subnet" "z1" {
  availability_zone = "${var.region}a"
  tags = {
    Name = "github-audit-prod-2a"
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }
}

resource "aws_default_subnet" "z2" {
  availability_zone = "${var.region}b"
  tags = {
    Name = "github-audit-prod-2b"
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }
}

resource "aws_default_subnet" "z3" {
  availability_zone = "${var.region}c"
  tags = {
    Name = "github-audit-prod-2c"
    Service = "${var.Service}"
    Environment = "${var.Environment}"
    SvcOwner = "${var.SvcOwner}"
    DeployedUsing = "${var.DeployedUsing}"
    SvcCodeURL = "${var.SvcCodeURL}"
  }
}
