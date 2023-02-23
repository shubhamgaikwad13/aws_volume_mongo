import boto3
from settings import AWS_KEY, AWS_SECRET_ACCESS_KEY
import json
from bson import json_util

def parameter_type_error_message(param, param_type):
    return f"Value for parameter '{param}' must be a {param_type}."


def get_ec2_client(region):

    ec2_client = boto3.client('ec2', aws_access_key_id=AWS_KEY,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=region)

    return ec2_client


def get_ec2_resource(region):

    ec2_resource = boto3.resource('ec2', aws_access_key_id=AWS_KEY,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=region)

    return ec2_resource


def parse_json(data):
    return json.loads(json_util.dumps(data))