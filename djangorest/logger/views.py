"""Модуль views для обработки REST API запросов в Django REST Framework.

Содержит view-функции для проксирования запросов к FastAPI и получения файлов из S3.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
import boto3
import os
from django.conf import settings


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def proxy_view(request, path):
    """Проксирует HTTP-запросы к FastAPI по указанному пути.

    Args:
        request: HTTP-запрос.
        path: Путь для перенаправления запроса к FastAPI.

    Returns:
        Response: Ответ от FastAPI в формате JSON.
    """
    fastapi_url = f"{os.getenv('FASTAPI_URL')}/{path}"
    headers = {'Content-Type': 'application/json'}

    if request.method == 'GET':
        response = requests.get(fastapi_url, params=request.GET, headers=headers)
    elif request.method == 'POST':
        response = requests.post(fastapi_url, json=request.data, headers=headers)
    elif request.method == 'DELETE':
        response = requests.delete(fastapi_url, headers=headers)

    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def s3_get_view(request):
    """Получает файл из S3 storage по указанному doc_id.

    Args:
        request: HTTP-запрос, содержащий параметр doc_id.

    Returns:
        Response: Содержимое файла в случае успеха или сообщение об ошибке.
    """
    doc_id = request.GET.get('doc_id')
    if not doc_id:
        return Response({'error': 'doc_id required'}, status=400)

    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv('S3_URL'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    try:
        response = s3.get_object(Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'), Key=f'documents/{doc_id}')
        return Response({'content': response['Body'].read().decode('utf-8')}, status=200)
    except s3.exceptions.NoSuchKey:
        return Response({'error': 'File not found'}, status=404)
