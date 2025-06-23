from django.db import models
from django.contrib.auth.models import User

class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    ip = models.CharField(max_length=45)
    timestamp = models.DateTimeField(auto_now_add=True)
    service = models.CharField(max_length=50)
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    status = models.IntegerField()
    location = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'docmagic_djangorest_log'
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'

    def __str__(self):
        return f'Log {self.id} - {self.service} {self.endpoint}'
