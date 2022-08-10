#!/usr/bin/env python3

import boto3
import botocore
import jinja2
import os
import sys
import yaml
import json
import datetime
from dateutil.tz import tzlocal


def main():
    if "AWS_PROFILE" in os.environ:
        secrets_manager = boto3.client("secretsmanager")
    elif "AWS_SECRETS_ROLE" in os.environ:
        secrets_session = assumed_role_session(os.environ["AWS_SECRETS_ROLE"])
    else:
        secrets_manager = secrets_session.client("secretsmanager")

    try:
        terraform_secret = secrets_manager.get_secret_value(
            SecretId="burendo-terraform-secrets")
       
    except botocore.exceptions.ClientError as e:
        error_message = e.response["Error"]["Message"]
        if "The security token included in the request is invalid" in error_message:
            print(
                "ERROR: Invalid security token used when calling AWS SSM. Have you run `aws-sts` recently?"
            )
        else:
            print("ERROR: Problem calling AWS SSM: {}".format(error_message))
        sys.exit(1)

    config_data = yaml.load(terraform_secret['SecretBinary'], Loader=yaml.FullLoader)
    config_data['terraform'] = json.loads(terraform_secret['SecretBinary'])["terraform"]

    with open("terraform.tf.j2") as in_template:
        template = jinja2.Template(in_template.read())
    with open("terraform.tf", "w+") as terraform_tf:
        terraform_tf.write(template.render(config_data))
    with open("variables.tf.j2") as in_template:
        template = jinja2.Template(in_template.read())
    with open("variables.tf", "w+") as terraform_tf:
        terraform_tf.write(template.render(config_data))
    with open("locals.tf.j2") as in_template:
        template = jinja2.Template(in_template.read())
    with open("locals.tf", "w+") as terraform_tf:
        terraform_tf.write(template.render(config_data))
    print("Terraform config successfully created")


def assumed_role_session(role_arn: str, base_session: botocore.session.Session = None):
    base_session = base_session or boto3.session.Session()._session
    fetcher = botocore.credentials.AssumeRoleCredentialFetcher(
        client_creator=base_session.create_client,
        source_credentials=base_session.get_credentials(),
        role_arn=role_arn,
        extra_args={
            #    'RoleSessionName': None # set this if you want something non-default
        },
    )
    creds = botocore.credentials.DeferredRefreshableCredentials(
        method="assume-role",
        refresh_using=fetcher.fetch_credentials,
        time_fetcher=lambda: datetime.datetime.now(tzlocal()),
    )
    botocore_session = botocore.session.Session()
    botocore_session._credentials = creds
    return boto3.Session(botocore_session=botocore_session)


if __name__ == "__main__":
    main()
