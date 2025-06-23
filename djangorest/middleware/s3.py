import uuid
import logging
from boto3.session import Session
from django.http import JsonResponse
from logger.models import Log

logger = logging.getLogger(__name__)

class S3Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and 'file' in request.FILES:
            try:
                file = request.FILES['file']
                file_id = str(uuid.uuid4())
                session = Session(
                    aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
                    aws_secret_access_key=os.getenv('S3_SECRET_KEY')
                )
                s3 = session.client('s3', endpoint_url=os.getenv('S3_ENDPOINT_URL'))
                s3.upload_fileobj(file, os.getenv('S3_BUCKET'), file_id)
                Log.objects.create(
                    user=request.user,
                    ip=request.META.get('REMOTE_ADDR', ''),
                    service='djangorest',
                    endpoint=request.path,
                    method='POST',
                    status=200,
                    location=request.META.get('HTTP_X_FORWARDED_FOR', '')
                )
                request.s3_file_id = file_id
            except Exception as e:
                Log.objects.create(
                    user=request.user,
                    ip=request.META.get('REMOTE_ADDR', ''),
                    service='djangorest',
                    endpoint=request.path,
                    method='POST',
                    status=500,
                    location=request.META.get('HTTP_X_FORWARDED_FOR', '')
                )
                return JsonResponse({'error': str(e)}, status=500)
        return self.get_response(request)
