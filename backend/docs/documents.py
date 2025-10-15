"""
Lambda function pour gérer les documents (métadonnées)
Stockage des fichiers sur S3, métadonnées dans DynamoDB
"""
import boto3
import json
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
table_name = os.environ.get('DOCUMENTS_TABLE', 'delphinium-documents')
bucket_name = os.environ.get('DOCUMENTS_BUCKET', 'delphinium-documents')

# Créer la table si elle n'existe pas
try:
    table = dynamodb.Table(table_name)
    table.load()
except:
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'documentId', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'documentId', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()

def lambda_handler(event, context):
    """
    Gère les opérations sur les documents
    GET: Récupérer la liste des documents
    POST: Enregistrer les métadonnées d'un document
    """
    http_method = event.get('httpMethod')
    path = event.get('path', '')

    try:
        if 'upload-url' in path:
            return generate_upload_url(event)
        elif 'download-url' in path:
            return generate_download_url(event)
        elif http_method == 'GET':
            return get_documents()
        elif http_method == 'POST':
            return save_document_metadata(event)
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

def get_documents():
    """Récupère tous les documents"""
    response = table.scan()
    documents = response.get('Items', [])

    # Trier par date d'upload décroissante
    documents.sort(key=lambda x: x.get('uploadedAt', 0), reverse=True)

    return {
        'statusCode': 200,
        'body': json.dumps({'documents': documents}, default=str)
    }

def generate_upload_url(event):
    """Génère une URL présignée pour uploader un document sur S3"""
    body = json.loads(event.get('body', '{}'))

    document_id = str(uuid.uuid4())
    file_name = body.get('fileName')
    file_type = body.get('fileType')

    # Générer une clé S3 unique
    s3_key = f"documents/{document_id}/{file_name}"

    # Créer une URL présignée pour l'upload
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': bucket_name,
            'Key': s3_key,
            'ContentType': file_type
        },
        ExpiresIn=3600  # 1 heure
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'uploadUrl': presigned_url,
            'documentId': document_id,
            's3Key': s3_key
        })
    }

def save_document_metadata(event):
    """Enregistre les métadonnées d'un document dans DynamoDB"""
    body = json.loads(event.get('body', '{}'))

    document = {
        'documentId': body.get('documentId'),
        'fileName': body.get('fileName'),
        'name': body.get('name'),
        'category': body.get('category'),
        'description': body.get('description'),
        's3Key': body.get('s3Key'),
        'uploadedBy': body.get('uploadedBy', 'Admin'),
        'uploadedAt': int(datetime.now().timestamp() * 1000)
    }

    table.put_item(Item=document)

    return {
        'statusCode': 201,
        'body': json.dumps({'document': document}, default=str)
    }

def generate_download_url(event):
    """Génère une URL présignée pour télécharger un document depuis S3"""
    document_id = event.get('pathParameters', {}).get('documentId')

    if not document_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Document ID required'})
        }

    # Récupérer les métadonnées du document
    response = table.get_item(Key={'documentId': document_id})

    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Document not found'})
        }

    document = response['Item']
    s3_key = document.get('s3Key')

    # Créer une URL présignée pour le téléchargement
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': s3_key
        },
        ExpiresIn=3600  # 1 heure
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'downloadUrl': presigned_url})
    }

