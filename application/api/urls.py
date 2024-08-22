from django.urls import path, include

urlpatterns = [
    path('', include('application.crypto.urls')),
]
