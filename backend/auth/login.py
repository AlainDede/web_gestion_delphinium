"""
Lambda function for user authentication using AWS Cognito.
"""
import boto3
import os

def lambda_handler(event, context):
    client = boto3.client('cognito-idp')
    user_pool_id = os.environ['COGNITO_USER_POOL_ID']
    client_id = os.environ['COGNITO_CLIENT_ID']
    userid = event.get('userid')
    password = event.get('password')
    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': userid,
                'PASSWORD': password
            }
        )
        return {
            'statusCode': 200,
            'body': response['AuthenticationResult']
        }
    except client.exceptions.NotAuthorizedException:
        return {
            'statusCode': 401,
            'body': 'Invalid credentials'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

