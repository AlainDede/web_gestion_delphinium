"""
Lambda function pour gérer les demandes d'accès au site
"""
import boto3
import json
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

# Créer la table si elle n'existe pas
table_name = os.environ.get('ACCESS_REQUESTS_TABLE', 'delphinium-access-requests')
try:
    table = dynamodb.Table(table_name)
    table.load()
except:
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'requestId', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'requestId', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()

def lambda_handler(event, context):
    """
    Gère les demandes d'accès au site
    POST: Créer une nouvelle demande d'accès
    GET: Récupérer toutes les demandes (admin uniquement)
    """
    http_method = event.get('httpMethod')

    try:
        if http_method == 'POST':
            return create_access_request(event)
        elif http_method == 'GET':
            return get_access_requests()
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

def create_access_request(event):
    """Crée une nouvelle demande d'accès"""
    body = json.loads(event.get('body', '{}'))

    request_id = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp() * 1000)

    access_request = {
        'requestId': request_id,
        'firstName': body.get('firstName'),
        'lastName': body.get('lastName'),
        'email': body.get('email'),
        'phone': body.get('phone'),
        'address': body.get('address'),
        'apartmentNumber': body.get('apartmentNumber'),
        'userType': body.get('userType'),
        'companyName': body.get('companyName'),
        'reason': body.get('reason'),
        'message': body.get('message'),
        'status': 'pending',
        'createdAt': timestamp
    }

    table.put_item(Item=access_request)

    # Envoyer une notification aux administrateurs (optionnel)
    try:
        topic_arn = os.environ.get('ADMIN_NOTIFICATION_TOPIC')
        if topic_arn:
            sns_client.publish(
                TopicArn=topic_arn,
                Subject='Nouvelle demande d\'accès - Delphinium',
                Message=f"Nouvelle demande d'accès reçue:\n"
                        f"Nom: {body.get('firstName')} {body.get('lastName')}\n"
                        f"Email: {body.get('email')}\n"
                        f"Type: {body.get('userType')}\n"
            )
    except Exception as e:
        print(f"Error sending notification: {e}")

    return {
        'statusCode': 201,
        'body': json.dumps({'request': access_request}, default=str)
    }

def get_access_requests():
    """Récupère toutes les demandes d'accès (admin uniquement)"""
    # TODO: Vérifier le rôle de l'utilisateur via le token JWT

    response = table.scan()
    requests = response.get('Items', [])

    # Trier par date de création décroissante
    requests.sort(key=lambda x: x.get('createdAt', 0), reverse=True)

    return {
        'statusCode': 200,
        'body': json.dumps({'requests': requests}, default=str)
    }
"""
Lambda function pour gérer les threads du newsgroup (forum de discussion)
"""
import boto3
import json
import os
import uuid
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('NEWSGROUP_TABLE', 'delphinium-newsgroup'))

def lambda_handler(event, context):
    """
    Gère les opérations CRUD sur les threads du newsgroup
    GET: Récupérer tous les threads
    POST: Créer un nouveau thread
    """
    http_method = event.get('httpMethod')

    try:
        if http_method == 'GET':
            return get_threads()
        elif http_method == 'POST':
            return create_thread(event)
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

def get_threads():
    """Récupère tous les threads du forum"""
    response = table.scan()
    threads = response.get('Items', [])

    # Trier par timestamp décroissant
    threads.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

    return {
        'statusCode': 200,
        'body': json.dumps({'threads': threads}, default=str)
    }

def create_thread(event):
    """Crée un nouveau thread de discussion"""
    body = json.loads(event.get('body', '{}'))

    # Récupérer l'auteur depuis le token JWT (simplifié ici)
    author = body.get('author', 'Anonymous')

    thread_id = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp() * 1000)

    thread = {
        'threadId': thread_id,
        'title': body.get('title'),
        'content': body.get('content'),
        'author': author,
        'timestamp': timestamp,
        'replies': []
    }

    table.put_item(Item=thread)

    return {
        'statusCode': 201,
        'body': json.dumps({'thread': thread}, default=str)
    }

