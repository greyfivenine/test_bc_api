from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('website.swagger_urls')),
    path('rabbit-hole/', admin.site.urls),
    path('api/', include('application.api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
