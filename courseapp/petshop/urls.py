# petshop/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("profil-tamamla/", views.petshop_profil_tamamla, name="petshop_profil_tamamla"),
]
