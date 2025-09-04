# etiket/urls.py
from django.urls import path
from . import views

app_name = "etiket"

urlpatterns = [
    path("lookup/", views.serial_number_lookup_view, name="lookup"),  # Türkçe içerikli arama formu
    path("serial/<str:serial_number>/", views.qr_by_serial_view, name="qr_by_serial"),  # Künye numarası ile yönlendirme
    path("<uuid:tag_id>/", views.qr_landing_view, name="qr_landing"),  # Ana QR açılış sayfası
    path("<uuid:tag_id>/download/", views.qr_download_view, name="qr_download"),  # QR kod indir
    path("<uuid:tag_id>/location/", views.qr_notify_location, name="qr_notify_location"),  # Konum bildirimi
]
