# quotes-api-new-relic

This is a simple REST API that fetches, parses, and saves Quotes from the website https://quotes.toscrape.com/random and integrates with a New Relic Account for telemetry monitoring.

### Setup 

First create a Cross Account IAM Role for New Relic allowing ReadOnly access. For this there is a Terraform script in main.tf which also saves the New Relic ingestion API key as an AWS Secrets Manager secret. The policy of the Secret is accessible via an SSM Parameter and consume in the AWS SAM based REST API.

```
terraform init
terraform plan -out plan.tfplan
terraform apply plan.tfplan
```

* IAM Role for New Relic Account with ReadOnly Access
* Secrets Manager secret for New Relic account ID and API Key
* SSM Parameter for IAM Policy for accessing Secret

Next deploy the SAM based Serverless REST API.

```
sam build --use-container
sam deploy --guided
```
