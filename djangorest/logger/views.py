import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from boto3.session import Session
from .models import Log

class S3GetView(APIView):
    def get(self, request):
        file_id = request.query_params.get('file_id')
        if not file_id:
            return Response({'error': 'File ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        cache_key = f's3_file_{file_id}'
        cached_file = cache.get(cache_key)
        if cached_file:
            return Response({'file': cached_file}, status=status.HTTP_200_OK)
        try:
            session = Session(
                aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
                aws_secret_access_key=os.getenv('S3_SECRET_KEY')
            )
            s3 = session.client('s3', endpoint_url=os.getenv('S3_ENDPOINT_URL'))
            response = s3.get_object(Bucket=os.getenv('S3_BUCKET'), Key=file_id)
            file_data = response['Body'].read().decode('utf-8')
            cache.set(cache_key, file_data, timeout=3600)
            Log.objects.create(
                user=request.user,
                ip=request.META.get('REMOTE_ADDR', ''),
                service='djangorest',
                endpoint='/s3/get',
                method='GET',
                status=200,
                location=request.META.get('HTTP_X_FORWARDED_FOR', '')
            )
            return Response({'file': file_data}, status=status.HTTP_200_OK)
        except Exception as e:
            Log.objects.create(
                user=request.user,
                ip=request.META.get('REMOTE_ADDR', ''),
                service='djangorest',
                endpoint='/s3/get',
                method='GET',
                status=404,
                location=request.META.get('HTTP_X_FORWARDED_FOR', '')
            )
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

class S3DeleteView(APIView):
    def delete(self, request):
        file_id = request.query_params.get('file_id')
        if not file_id:
            return Response({'error': 'File ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            session = Session(
                aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
                aws_secret_access_key=os.getenv('S3_SECRET_KEY')
            )
            s3 = session.client('s3', endpoint_url=os.getenv('S3_ENDPOINT_URL'))
            s3.delete_object(Bucket=os.getenv('S3_BUCKET'), Key=file_id)
            cache.delete(f's3_file_{file_id}')
            Log.objects.create(
                user=request.user,
                ip=request.META.get('REMOTE_ADDR', ''),
                service='djangorest',
                endpoint='/s3/delete',
                method='DELETE',
                status=200,
                location=request.META.get('HTTP_X_FORWARDED_FOR', '')
            )
            return Response({'message': 'File deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            Log.objects.create(
                user=request.user,
                ip=request.META.get('REMOTE_ADDR', ''),
                service='djangorest',
                endpoint='/s3/delete',
                method='DELETE',
                status=404,
                location=request.META.get('HTTP_X_FORWARDED_FOR', '')
            )
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

class ProxyView(APIView):
    def get(self, request):
        return self._proxy_request(request, 'GET')
    def post(self, request):
        return self._proxy_request(request, 'POST')
    def delete(self, request):
        return self._proxy_request(request, 'DELETE')

    def _proxy_request(self, request, method):
        fastapi_url = os.getenv('FASTAPI_URL', 'http://fastapi:8080')
        endpoint = request.query_params.get('endpoint', '')
        cache_key = f'proxy_{method}_{endpoint}_{request.user.id}'
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)
        try:
            headers = {'Authorization': request.META.get('HTTP_AUTHORIZATION', '')}
            url = f'{fastapi_url}/{endpoint}'
            if method == 'GET':
                response = requests.get(url, headers=headers, params=request.query_params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=request.data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=request.query_params)
            response_data = response.json()
            cache.set(cache_key, response_data, timeout=3600)
            Log.objects.create(
                user=request.user,
                ip=request.META.get('REMOTE_ADDR', ''),
                service='djangorest',
                endpoint='/proxy',
                method=method,
                status=response.status_code,
                location=request.META.get('HTTP_X_FORWARDED_FOR', '')
            )
            return Response(response_data, status=response.status_code)
        except Exception as e:
            Log.objects.create(
                user=request.user,
                ip=request.META.get('REMOTE_ADDR', ''),
                service='djangorest',
                endpoint='/proxy',
                method=method,
                status=500,
                location=request.META.get('HTTP_X_FORWARDED_FOR', '')
            )
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
