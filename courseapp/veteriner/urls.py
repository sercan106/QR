# veteriner/urls.py

from django.urls import path
from . import views

app_name = "veteriner"

urlpatterns = [
    path("profil/tamamla/", views.veteriner_profil_tamamla, name="veteriner_profil_tamamla"),
    path("panel/", views.veteriner_paneli, name="veteriner_paneli"),

    # Hepsini gör (liste) sayfaları
    path("tahsisler/", views.tahsis_listesi, name="tahsis_listesi"),
    path("satislar/", views.satis_listesi, name="satis_listesi"),
    path("siparisler/", views.siparis_listesi, name="siparis_listesi"),
]
