from enum import Enum
import boto3
__secrets_client = boto3.client('secretsmanager')
__cached_secrets = {}


class Secret(Enum):
    DB = 1
    PASSWORD = 2


def get_secret(name: Secret) -> {}:
    secret_id = get_secret_id(name)
    if secret_id not in __cached_secrets:
        __cached_secrets[secret_id] = __secrets_client.get_secret_value(SecretId=secret_id)
    return __cached_secrets[secret_id]


def get_secret_id(name: Secret) -> str:
    match name:
        case Secret.DB: return "prod/beansql"
        case Secret.PASSWORD: return "prod/api-password"