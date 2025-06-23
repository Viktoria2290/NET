from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.http import JsonResponse

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()

    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            try:
                token = auth_header.split(' ')[1]
                validated_token = self.jwt_authenticator.get_validated_token(token)
                request.user = self.jwt_authenticator.get_user(validated_token)
            except (InvalidToken, AuthenticationFailed) as e:
                return JsonResponse({'error': str(e)}, status=401)
        return self.get_response(request)
