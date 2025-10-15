"""
Lambda function pour gérer les réponses aux threads du newsgroup
"""
import boto3
import json
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('NEWSGROUP_TABLE', 'delphinium-newsgroup'))

def lambda_handler(event, context):
    """
    Ajoute une réponse à un thread existant
    POST /newsgroup/threads/{threadId}/replies
    """
    thread_id = event.get('pathParameters', {}).get('threadId')

    if not thread_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Thread ID required'})
        }

    try:
        body = json.loads(event.get('body', '{}'))
        author = body.get('author', 'Anonymous')

        # Récupérer le thread existant
        response = table.get_item(Key={'threadId': thread_id})

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Thread not found'})
            }

        thread = response['Item']

        # Créer la réponse
        reply = {
            'replyId': str(uuid.uuid4()),
            'content': body.get('content'),
            'author': author,
            'timestamp': int(datetime.now().timestamp() * 1000)
        }

        # Ajouter la réponse au thread
        if 'replies' not in thread:
            thread['replies'] = []
        thread['replies'].append(reply)

        # Mettre à jour le thread
        table.put_item(Item=thread)

        return {
            'statusCode': 201,
            'body': json.dumps({'reply': reply}, default=str)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

