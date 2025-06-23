from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_view, name='upload'),
    path('documents/', views.document_list, name='documents'),
    path('delete/', views.delete_view, name='delete'),
    path('analyse/', views.analyse_view, name='analyse'),
    path('text/<int:doc_id>/', views.get_text, name='text'),
    path('cart/', views.cart_view, name='cart'),
    path('payment/<int:cart_id>/', views.payment_view, name='payment'),
    path('api/upload/', views.upload_doc_api, name='upload_doc_api'),
    path('api/delete/<int:doc_id>/', views.doc_delete_api, name='doc_delete_api'),
    path('api/analyse/', views.doc_analyse_api, name='doc_analyse_api'),
    path('api/text/<int:doc_id>/', views.get_text_api, name='get_text_api'),
]
