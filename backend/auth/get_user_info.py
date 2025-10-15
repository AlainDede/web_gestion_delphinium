"""
Lambda function pour récupérer les informations de l'utilisateur connecté
et vérifier ses groupes/rôles dans AWS Cognito.
"""
import boto3
import os
from jose import jwt

def lambda_handler(event, context):
    """
    Récupère les informations de l'utilisateur à partir de son token JWT.
    Retourne le nom d'utilisateur, l'email et les groupes auxquels il appartient.
    """
    try:
        # Récupération du token depuis les headers
        auth_header = event.get('headers', {}).get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return {
                'statusCode': 401,
                'body': 'Token manquant ou invalide'
            }

        token = auth_header.replace('Bearer ', '')

        # Décodage du token (sans vérification de signature pour cette démo)
        # En production, utilisez la vérification complète avec les clés publiques Cognito
        decoded_token = jwt.get_unverified_claims(token)

        username = decoded_token.get('cognito:username')
        email = decoded_token.get('email')
        groups = decoded_token.get('cognito:groups', [])

        # Récupération des informations détaillées depuis Cognito
        client = boto3.client('cognito-idp')
        user_pool_id = os.environ['COGNITO_USER_POOL_ID']

        user_info = client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=username
        )

        # Récupération des groupes de l'utilisateur
        user_groups = client.admin_list_groups_for_user(
            UserPoolId=user_pool_id,
            Username=username
        )

        return {
            'statusCode': 200,
            'body': {
                'username': username,
                'email': email,
                'groups': [g['GroupName'] for g in user_groups['Groups']],
                'userAttributes': user_info.get('UserAttributes', [])
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
boto3>=1.26.0
python-jose[cryptography]>=3.3.0

