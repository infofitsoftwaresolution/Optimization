"""Bedrock client factory (scaffold)."""

import boto3
from botocore.config import Config
from typing import Optional
import os


def get_bedrock_client(region_name: Optional[str] = None):
    """
    Get Bedrock client using AWS credentials from environment variables,
    ~/.aws/credentials, or IAM role.
    
    Credentials are configured via:
    - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    - AWS credentials file (~/.aws/credentials)
    - IAM role (when running on EC2/ECS/Lambda)
    """
    cfg = Config(retries={"max_attempts": 3, "mode": "standard"}, read_timeout=60)
    
    # Use default AWS credentials (environment variables, ~/.aws/credentials, IAM role)
    if region_name:
        return boto3.client("bedrock-runtime", region_name=region_name, config=cfg)
    return boto3.client("bedrock-runtime", config=cfg)


