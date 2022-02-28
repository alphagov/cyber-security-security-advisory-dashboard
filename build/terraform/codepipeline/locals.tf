locals {
  tags = {
    Service       = "github-audit"
    SvcOwner      = "cyber.security@digital.cabinet-office.gov.uk"
    Environment   = var.environment
    DeployedUsing = "Terraform_v14"
    SvcCodeURL    = "https://github.com/alphagov/cyber-security-security-advisory-dashboard"
  }
}
