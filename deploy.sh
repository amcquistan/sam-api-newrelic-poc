#!/bin/bash

if [ -z $NR_ACCT ]; then
  echo "Missing New Relic Account"
  exit 1
fi

if [ -z $AWS_PROFILE ]; then
  echo "Missing AWS Profile"
  exit 1
fi

if [ -z $AWS_REGION ]; then
  echo "Missing AWS Region"
  exit 1
fi

if [ -z $STACK_NAME ]; then
  echo "Missing Stack Name"
  exit 1
fi


sam deploy --guided \
    --stack-name $STACK_NAME \
    --profile $AWS_PROFILE \
    --region $AWS_REGION \
    --parameter-overrides NewRelicAcctID=$NR_ACCT
