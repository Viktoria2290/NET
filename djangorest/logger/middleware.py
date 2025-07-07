import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('djangorest')

class LoggingMiddleware:
    """Middleware для логирования HTTP-запросов и ответов с использованием кэширования.

    Логирует информацию о пользователе, IP-адресе, методе запроса, endpoint и статусе ответа.
    Использует cache для хранения ответов и предотвращения повторной обработки запросов.
    """
    def __init__(self, get_response):
        """Инициализирует middleware с функцией обработки ответа.

        Args:
            get_response: Функция, которая будет вызвана для получения ответа.
        """
        self.get_response = get_response

    def __call__(self, request):
        """Обрабатывает входящий запрос, логирует его и кэширует ответ.

        Args:
            request: HTTP-запрос.

        Returns:
            Response: Ответ сервера, либо из cache, либо после обработки.
        """
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        endpoint = request.path
        method = request.method
        location = request.META.get('HTTP_X_FORWARDED_FOR', 'unknown')

        cache_key = f'request_{method}_{endpoint}_{user}'
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f'Cache hit: {cache_key}', extra={
                'user': user, 'ip': ip, 'endpoint': endpoint, 'method': method, 'status': 200, 'location': location
            })
            return cached_response

        response = self.get_response(request)
        status = response.status_code

        logger.info(f'Request processed: {method} {endpoint}', extra={
            'user': user, 'ip': ip, 'endpoint': endpoint, 'method': method, 'status': status, 'location': location
        })

        cache.set(cache_key, response, timeout=300)
        return response
