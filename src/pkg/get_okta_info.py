"""
Get Okta User Information for a specific Okta App. Organize and upload that info
to S3
"""

import os
import traceback
import json
import boto3
import urllib3
from ast_de_python_utils.log_utils import setup_logger


# Logging
LOGGER = setup_logger()

FAILURE_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps("Okta User Information Retrieval execution has failed"),
}

SUCCESS_RESPONSE = {
    'statusCode': 200,
    'body': json.dumps("Okta User Information Retrieval execution complete"),
}

# Boto3
S3_RESOURCE = boto3.resource('s3')
SECRETS_CLIENT = boto3.client('secretsmanager')

# Environment Variables
BUCKET = os.environ['QS_GOVERNANCE_BUCKET']
KEY = os.environ['QS_USER_GOVERNANCE_KEY']
OKTA_SECRET = os.environ['OKTA_SECRET']

# Urllib3
HTTP = urllib3.PoolManager()

# Okta Specific Secrets
response = SECRETS_CLIENT.get_secret_value(SecretId=OKTA_SECRET)
OKTA_ACCT_ID = json.loads(response['SecretString'])['okta-account-id-secret']
OKTA_APP_ID = json.loads(response['SecretString'])['okta-app-id-secret']
OKTA_APP_TOKEN = json.loads(response['SecretString'])['okta-app-token-secret']
OKTA_URL = f"https://{OKTA_ACCT_ID}.okta.com/api/v1/apps/{OKTA_APP_ID}/users"
OKTA_AUTH = f"SSWS {OKTA_APP_TOKEN}"


def handler(event, _):
    """
    - Get User Info from Okta via API
    - Build User Governance Manifest File
    - Upload the Manifest to S3
    """

    LOGGER.info(f"event: {event}")

    try:
        users = get_users()
        manifest = build_user_governance_manifest(users)
        upload_to_s3(manifest)
        return SUCCESS_RESPONSE

    except Exception as err:
        LOGGER.error(traceback.format_exc())
        raise Exception(FAILURE_RESPONSE) from err


def get_users():
    """
    Use urllib3 to make a REST call to get list of Okta
    Users for a given Okta Application
    """
    okta_users_request = HTTP.request(
        'GET',
        OKTA_URL,
        headers={'Content-Type': 'application/json', 'Authorization': OKTA_AUTH},
        retries=False,
    )
    LOGGER.info(f"Retrieved Okta Users Information from {OKTA_URL}")
    return json.loads(okta_users_request.data.decode('utf-8'))


def build_user_governance_manifest(users):
    """
    Build QuickSight Users manifest from the HTTP Request json
    """
    user_manifest = {"users": []}

    for usr in users:
        profile = usr['profile'].keys()
        creds = usr['credentials'].keys()

        # only add fully specd users
        if (
                'userName' in creds
                and 'department' in profile
                and 'userType' in profile
                and 'email' in profile
                and 'organization' in profile
        ):
            user_manifest['users'].append(
                {
                    "username": usr['credentials']['userName'],
                    "namespace": usr['profile']['organization'],
                    "groups": usr['profile']['department'],
                    "role": usr['profile']['userType'],
                    "email": usr['profile']['email'],
                }
            )
    return user_manifest


def upload_to_s3(json_data):
    """
    upload json data to an S3 object
    """
    s3object = S3_RESOURCE.Object(BUCKET, KEY)
    s3object.put(Body=(bytes(json.dumps(json_data).encode('UTF-8'))))
    LOGGER.info(f"Manifest uploaded to s3://{BUCKET}/{KEY}")
