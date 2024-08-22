from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views as token_views


router = DefaultRouter()
router.register(r'token', token_views.TokenViewSet, basename='token')

urlpatterns = [
    path('', include(router.urls)),
]
