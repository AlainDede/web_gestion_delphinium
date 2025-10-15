"""
Lambda function pour gérer les événements du calendrier
"""
import boto3
import json
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('CALENDAR_TABLE', 'delphinium-calendar'))

def lambda_handler(event, context):
    """
    Gère les opérations CRUD sur les événements du calendrier
    GET: Récupérer les événements (filtrage par mois/année)
    POST: Créer un nouvel événement (admin uniquement)
    """
    http_method = event.get('httpMethod')

    try:
        if http_method == 'GET':
            return get_events(event)
        elif http_method == 'POST':
            return create_event(event)
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

def get_events(event):
    """Récupère les événements filtrés par mois et année"""
    query_params = event.get('queryStringParameters', {})
    year = query_params.get('year')
    month = query_params.get('month')

    response = table.scan()
    events = response.get('Items', [])

    # Filtrer par mois/année si spécifié
    if year and month:
        events = [
            e for e in events
            if e.get('eventDate', '').startswith(f"{year}-{month.zfill(2)}")
        ]

    # Trier par date
    events.sort(key=lambda x: x.get('eventDate', ''))

    return {
        'statusCode': 200,
        'body': json.dumps({'events': events}, default=str)
    }

def create_event(event):
    """Crée un nouvel événement (admin uniquement)"""
    # TODO: Vérifier le rôle de l'utilisateur via le token JWT

    body = json.loads(event.get('body', '{}'))

    event_id = str(uuid.uuid4())

    calendar_event = {
        'eventId': event_id,
        'title': body.get('title'),
        'description': body.get('description'),
        'eventDate': body.get('eventDate'),  # Format: YYYY-MM-DD
        'time': body.get('time'),
        'location': body.get('location'),
        'createdBy': body.get('author', 'Admin')
    }

    table.put_item(Item=calendar_event)

    return {
        'statusCode': 201,
        'body': json.dumps({'event': calendar_event}, default=str)
    }

