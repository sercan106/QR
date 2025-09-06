# veteriner/urls.py

from django.urls import path
from . import views

app_name = "veteriner"

urlpatterns = [
    path("profil/tamamla/", views.veteriner_profil_tamamla, name="veteriner_profil_tamamla"),
    path("panel/", views.veteriner_paneli, name="veteriner_paneli"),
]