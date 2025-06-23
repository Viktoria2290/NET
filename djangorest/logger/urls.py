from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('s3/get/', views.S3GetView.as_view(), name='s3_get'),
    path('s3/delete/', views.S3DeleteView.as_view(), name='s3_delete'),
    path('proxy/', views.ProxyView.as_view(), name='proxy'),
]
