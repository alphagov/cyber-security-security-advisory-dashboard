provider "aws" {
  region = "${var.region}"
}

provider "aws" {
  # us-east-1 instance
  region  = "us-east-1"
  alias   = "use1"
}