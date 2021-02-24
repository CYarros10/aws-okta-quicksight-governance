"""Constants file for resource naming and env values"""
import os

###################################
# Per Account/App Setup (Edit as Needed)
###################################
ACCOUNT = "012345678901"
OKTA_SECRET = "okta_info"
REGION = "us-east-1"
OKTA_IDP_NAME = "Okta"
CDK_ENV = {"account": ACCOUNT, "region": REGION}

###################################
# Manifest Data
###################################
QS_USER_GOVERNANCE_KEY = "qs-user-governance.json"
QS_ASSET_GOVERNANCE_KEY = "qs-asset-governance.json"

###################################
# Setting up repo paths
###################################
PATH_CDK = os.path.dirname(os.path.abspath(__file__))
PATH_ROOT = os.path.dirname(PATH_CDK)
PATH_SRC = os.path.join(PATH_ROOT, 'src')

###################################
# Project Specific Setup
###################################
PROJECT = "QSGovernance"
OKTA_ROLE_NAME = "FederatedQuickSightRole"