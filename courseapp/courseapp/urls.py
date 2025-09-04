# courseapp/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('anahtarlik.urls')),
    path('accaunt/', include('accaunt.urls')),
    path('shop/', include('shop.urls')),
    path('tag/', include('etiket.urls', namespace='etiket')),  # ✅ Etiket app'ini dahil ettik
    path('petpanel/', include('petpanel.urls')),  # ekli olmalı
]

# Medya ve statik dosyalar
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
