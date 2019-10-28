#Create Customer Managed KMS key
# resource "aws_kms_key" "prod_kms_key" {
#   description             = "KMS key to encrypt and decrypt Github API token"
#   deletion_window_in_days = 7
#   enable_key_rotation = true
# }

# resource "aws_kms_alias" "prod_kms_alias" {
# name          = "alias/security-advisories-prod-kms"
# target_key_id = "${aws_kms_key.prod_kms_key.key_id}"
# }

# resource "aws_kms_grant" "prod_kms_grant" {
# name              = "security-advisories-kms-grant"
# key_id            = "${aws_kms_key.prod_kms_key.key_id}"
# grantee_principal = "${aws_iam_role.lambda-iam.arn}"
# operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
# }

data "aws_kms_secrets" "github_key" { # decrypts the key
    secret {
        name = "github_key"
        payload = "AQICAHhe01flQwZvqnxcRcriXcTn8QzO9B5PrggjEtFLxnGsSwGhx9NZkLHKsfr4AaF0MplCAAAAiDCBhQYJKoZIhvcNAQcGoHgwdgIBADBxBgkqhkiG9w0BBwEwHgYJYIZIAWUDBAEuMBEEDIWO4VVrz5kCj2FUNwIBEIBE7mON+d6P+9Jo3ogiMXHpGM/l64jU3IAqpXE2pE5Fn/Dmg2Tdavzpmlw3mDnSkdICweIW7Qc9cw2t4QjfPGcg6ttBTPM=" # from aws cli kms outpu
    }
}
