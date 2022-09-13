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
    if not ("AWS_PROFILE" in os.environ or "AWS_SECRETS_ROLE" in os.environ):
        print("ERROR: Missing environment variables. Must contain either AWS_PROFILE (local) or AWS_SECRETS_ROLE (GHA)")

    secrets_manager = boto3.client("secretsmanager")

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
    config_data['accounts'] = json.loads(terraform_secret['SecretBinary'])["accounts"]

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

if __name__ == "__main__":
    main()
