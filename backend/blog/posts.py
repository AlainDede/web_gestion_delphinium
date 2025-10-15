"""
Lambda function pour gérer les posts du blog
"""
import boto3
import json
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('BLOG_TABLE', 'delphinium-blog'))

def lambda_handler(event, context):
    """
    Gère les opérations CRUD sur les posts du blog
    GET: Récupérer tous les posts
    POST: Créer un nouveau post (admin/superadmin uniquement)
    """
    http_method = event.get('httpMethod')

    try:
        if http_method == 'GET':
            return get_posts()
        elif http_method == 'POST':
            return create_post(event)
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'message': 'Method not allowed'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_posts():
    """Récupère tous les posts du blog"""
    response = table.scan()
    posts = response.get('Items', [])

    # Trier par date de création décroissante
    posts.sort(key=lambda x: x.get('createdAt', 0), reverse=True)

    return {
        'statusCode': 200,
        'body': json.dumps({'posts': posts}, default=str)
    }

def create_post(event):
    """Crée un nouveau post de blog (admin uniquement)"""
    # TODO: Vérifier le rôle de l'utilisateur via le token JWT

    body = json.loads(event.get('body', '{}'))

    post_id = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp() * 1000)

    post = {
        'postId': post_id,
        'title': body.get('title'),
        'summary': body.get('summary'),
        'content': body.get('content'),
        'author': body.get('author', 'Admin'),
        'category': body.get('category', 'General'),
        'imageUrl': body.get('imageUrl'),
        'createdAt': timestamp
    }

    table.put_item(Item=post)

    return {
        'statusCode': 201,
        'body': json.dumps({'post': post}, default=str)
    }

