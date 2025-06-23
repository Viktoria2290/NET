import pytest
from django.contrib.auth.models import User
from docs.models import Docs, UsersToDocs, Price, Cart

@pytest.mark.django_db
def test_docs_model():
    doc = Docs.objects.create(
        file_path="/uploads/test.jpg",
        size=1024,
        text="Sample text",
        status="новый"
    )
    assert doc.__str__() == f"Документ {doc.id}"

@pytest.mark.django_db
def test_userstodocs_model():
    user = User.objects.create(username="testuser")
    doc = Docs.objects.create(file_path="/uploads/test.jpg", size=1024)
    user_doc = UsersToDocs.objects.create(username=user.username, docs=doc)
    assert user_doc.__str__() == f"{user.username} - {doc}"

@pytest.mark.django_db
def test_price_model():
    price = Price.objects.create(file_type="jpg", price=0.5)
    assert price.__str__() == "jpg: 0.5"

@pytest.mark.django_db
def test_cart_model():
    user = User.objects.create(username="testuser")
    doc = Docs.objects.create(file_path="/uploads/test.jpg", size=1024)
    cart = Cart.objects.create(user=user, docs=doc, order_price=10.0)
    assert cart.__str__() == f"Cart {cart.id} for {user.username}"
