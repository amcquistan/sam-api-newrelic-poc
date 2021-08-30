#!/bin/bash

# This script links the a NewRelic account to an AWS Account.
# The script is driven by environment variables populated
# via .env file

if [ -f .env ]; then
  source .env
fi


if [ -z $AWS_PROFILE ]; then
  echo "Missing AWS Profile"
  exit 1
fi

if [ -z $AWS_REGION ]; then
  echo "Missing AWS Region"
  exit 1
fi

if [ -z $NR_LICENSE ]; then
  echo "Missing New Relic Ingest License"
  exit 1
fi

if [ -z $NR_ACCT ]; then
  echo "Missing New Relic Account"
  exit 1
fi

echo "Using AWS_PROFILE $AWS_PROFILE"
echo "Using AWS_REGION $AWS_REGION"
echo "Using NR_LICENSE $NR_LICENSE"

if [ -f license-key-secret.yaml ]; then
  rm license-key-secret.yaml
fi

http --download https://raw.githubusercontent.com/newrelic/newrelic-lambda-cli/master/newrelic_lambda_cli/templates/license-key-secret.yaml


aws cloudformation create-stack --stack-name NewRelicLicenseKeySecret \
    --template-body file://license-key-secret.yaml \
    --profile $AWS_PROFILE \
    --region $AWS_REGION \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameters ParameterKey=LicenseKey,ParameterValue=$NR_LICENSE ParameterKey=NrAccountId,ParameterValue=$NR_ACCT
