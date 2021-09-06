
###################################################################################
# Providers
###################################################################################
provider "aws" {
    region     = "us-east-2"
}

###################################################################################
# Variables
###################################################################################

variable "newrelic_account_id" {}

variable "newrelic_ingest_key" {}

###################################################################################
# Data
###################################################################################

data "aws_iam_policy_document" "newrelic_policy_doc" {
  statement {
    sid = "TrustNewRelicAccount"
    actions = ["sts:AssumeRole"]
    principals {
      type = "AWS"
      identifiers = ["arn:aws:iam::754728514883:root"]
    }
    condition {
      test = "StringEquals"
      variable = "sts:ExternalId"
      values = [var.newrelic_account_id]
    }
  }
}

# data "aws_iam_policy_document" "newrelic_key_policy_doc" {
#   statement {
#     sid = "NewRelicSecretPolicy"
#     actions = ["secretsmanager:GetSecretValue"]
#     resources = ["*"]
#   }
# }

###################################################################################
# Resources
###################################################################################

resource "aws_iam_role" "newrelic_iam_role" {
  name = "newrelic-role"
  managed_policy_arns = [ "arn:aws:iam::aws:policy/ReadOnlyAccess" ]
  assume_role_policy = data.aws_iam_policy_document.newrelic_policy_doc.json
}

resource "aws_secretsmanager_secret" "newrelic_ingest_key" {
  name = "newrelic-ingest-key"
  description = "The New Relic license key, for sending telemetry"
}

resource "aws_secretsmanager_secret_version" "newrelic_ingest_key" {
  secret_id = aws_secretsmanager_secret.newrelic_ingest_key.id
  secret_string = "{ \"LicenseKey\": \"${var.newrelic_ingest_key}\", \"NrAccountId\": \"${var.newrelic_account_id}\" }"
}

resource "aws_secretsmanager_secret_policy" "newrelic_ingest_key" {
  secret_arn = aws_secretsmanager_secret.newrelic_ingest_key.arn
  policy = <<POLICY
  {
      "Version": "2012-10-17",
      "Statement": [{
          "Sid": "NewRelicSecretPolicy",
          "Effect": "Allow",
          "Principal": {
            "AWS": "*"
          },
          "Action": "secretsmanager:GetSecretValue",
          "Resource": ["${aws_secretsmanager_secret.newrelic_ingest_key.arn}"]
      }]
  }
  POLICY
}

resource "aws_ssm_parameter" "newrelic_secret_policy" {
  name = "newrelic-secret-key-policy"
  type = "String"
  value = aws_secretsmanager_secret_policy.newrelic_ingest_key.id
}


###################################################################################
# Output
###################################################################################

output "newrelic_iam_role" {
  value = aws_iam_role.newrelic_iam_role.arn
}

output "newrelic_ingest_key_secret_policy" {
  value = aws_secretsmanager_secret_policy.newrelic_ingest_key.id
}