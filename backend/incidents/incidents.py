"""
Lambda function pour gérer les incidents
"""
import boto3
import json
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('INCIDENTS_TABLE', 'delphinium-incidents'))

def lambda_handler(event, context):
    """
    Gère les opérations CRUD sur les incidents
    GET: Récupérer tous les incidents
    POST: Créer un nouvel incident
    PUT: Mettre à jour un incident (statut, priorité)
    """
    http_method = event.get('httpMethod')

    try:
        if http_method == 'GET':
            return get_incidents()
        elif http_method == 'POST':
            return create_incident(event)
        elif http_method == 'PUT':
            return update_incident(event)
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

def get_incidents():
    """Récupère tous les incidents"""
    response = table.scan()
    incidents = response.get('Items', [])

    # Trier par date de création décroissante
    incidents.sort(key=lambda x: x.get('createdAt', 0), reverse=True)

    return {
        'statusCode': 200,
        'body': json.dumps({'incidents': incidents}, default=str)
    }

def create_incident(event):
    """Crée un nouvel incident (admin uniquement)"""
    # TODO: Vérifier le rôle de l'utilisateur via le token JWT

    body = json.loads(event.get('body', '{}'))

    incident_id = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp() * 1000)

    incident = {
        'incidentId': incident_id,
        'title': body.get('title'),
        'description': body.get('description'),
        'priority': body.get('priority', 'medium'),  # low, medium, high
        'status': body.get('status', 'open'),  # open, in_progress, resolved
        'createdAt': timestamp,
        'createdBy': body.get('author', 'Admin'),
        'assignedTo': body.get('assignedTo'),
        'notes': []
    }

    table.put_item(Item=incident)

    return {
        'statusCode': 201,
        'body': json.dumps({'incident': incident}, default=str)
    }

def update_incident(event):
    """Met à jour un incident existant"""
    incident_id = event.get('pathParameters', {}).get('incidentId')

    if not incident_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Incident ID required'})
        }

    body = json.loads(event.get('body', '{}'))

    # Récupérer l'incident existant
    response = table.get_item(Key={'incidentId': incident_id})

    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Incident not found'})
        }

    incident = response['Item']

    # Mettre à jour les champs
    if 'status' in body:
        incident['status'] = body['status']
    if 'priority' in body:
        incident['priority'] = body['priority']
    if 'assignedTo' in body:
        incident['assignedTo'] = body['assignedTo']
    if 'note' in body:
        if 'notes' not in incident:
            incident['notes'] = []
        incident['notes'].append({
            'timestamp': int(datetime.now().timestamp() * 1000),
            'author': body.get('author', 'Admin'),
            'note': body['note']
        })

    incident['updatedAt'] = int(datetime.now().timestamp() * 1000)

    table.put_item(Item=incident)

    return {
        'statusCode': 200,
        'body': json.dumps({'incident': incident}, default=str)
    }

