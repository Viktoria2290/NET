from django.db import models
from django.contrib.auth.models import User

class Docs(models.Model):
    """Модель для хранения информации о загруженных документах.

    Attributes:
        file_path (CharField): Путь к файлу документа на сервере или в storage.
        size (FloatField): Размер файла в килобайтах.
        created_at (DateTimeField): Дата и время создания записи о документе.
    """
    file_path = models.CharField(max_length=255)
    size = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class UsersToDocs(models.Model):
    """Модель для связи пользователей с документами (many-to-many).

    Attributes:
        username (ForeignKey): Ссылка на модель User, указывающая на владельца документа.
        docs_id (ForeignKey): Ссылка на модель Docs, указывающая на документ.
    """
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    docs_id = models.ForeignKey(Docs, on_delete=models.CASCADE)

class Price(models.Model):
    """Модель для хранения цен на обработку документов в зависимости от их типа.

    Attributes:
        file_type (CharField): Тип файла (например, 'jpeg', 'png').
        price (FloatField): Цена за обработку файла в зависимости от его размера.
    """
    file_type = models.CharField(max_length=10)
    price = models.FloatField()

class Cart(models.Model):
    """Модель для хранения информации о корзине пользователя.

    Attributes:
        user_id (ForeignKey): Ссылка на модель User, указывающая на владельца корзины.
        docs_id (ForeignKey): Ссылка на модель Docs, указывающая на документ в корзине.
        order_price (FloatField): Стоимость обработки документа.
        payment (BooleanField): Статус оплаты (True, если оплачено).
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    docs_id = models.ForeignKey(Docs, on_delete=models.CASCADE)
    order_price = models.FloatField()
    payment = models.BooleanField(default=False)
