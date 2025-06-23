from django.db import models
from django.contrib.auth.models import User

class Docs(models.Model):
    file_path = models.CharField(max_length=255)
    size = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, default='')
    status = models.CharField(max_length=50, default='новый')

    class Meta:
        db_table = 'docmagic_djangocore_docs'
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    def __str__(self):
        return f'Документ {self.id}'

class UsersToDocs(models.Model):
    username = models.CharField(max_length=150)
    docs = models.ForeignKey(Docs, on_delete=models.CASCADE)

    class Meta:
        db_table = 'docmagic_djangocore_userstodocs'

    def __str__(self):
        return f'{self.username} - {self.docs}'

class Price(models.Model):
    file_type = models.CharField(max_length=10)
    price = models.FloatField()

    class Meta:
        db_table = 'docmagic_djangocore_price'

    def __str__(self):
        return f'{self.file_type}: {self.price}'

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    docs = models.ForeignKey(Docs, on_delete=models.CASCADE)
    order_price = models.FloatField()
    payment = models.BooleanField(default=False)

    class Meta:
        db_table = 'docmagic_djangocore_cart'

    def __str__(self):
        return f'Cart {self.id} for {self.user.username}'
