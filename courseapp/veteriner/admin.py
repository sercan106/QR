# veteriner/admin.py

from django.contrib import admin, messages
from django.utils import timezone
from .models import Veteriner, SiparisIstemi

@admin.register(Veteriner)
class VeterinerAdmin(admin.ModelAdmin):
    list_display = ("ad", "il", "ilce", "telefon", "odeme_modeli", "tahsis_sayisi", "satis_sayisi", "kalan_envanter_goster", "aktif")
    list_filter = ("aktif", "odeme_modeli", "il", "ilce")
    search_fields = ("ad", "telefon", "email", "il", "ilce")
    readonly_fields = ()
    ordering = ("-olusturulma",)

    def kalan_envanter_goster(self, obj):
        return obj.kalan_envanter
    kalan_envanter_goster.short_description = "Kalan Envanter"


@admin.register(SiparisIstemi)
class SiparisIstemiAdmin(admin.ModelAdmin):
    list_display = (
        "veteriner", "talep_edilen_adet", "talep_tarihi",
        "onaylandi", "kargolandimi", "kargo_sirketi", "kargo_takip_no",
    )
    list_filter = ("onaylandi", "kargolandimi", "kargo_sirketi", "talep_tarihi")
    search_fields = (
        "veteriner__ad", "veteriner__il", "veteriner__ilce",
        "kargo_takip_no", "il", "ilce", "adres_detay"
    )
    date_hierarchy = "talep_tarihi"
    actions = ["isaretle_onaylandi", "isaretle_kargolandı"]

    fieldsets = (
        ("Sipariş", {"fields": ("veteriner", "talep_edilen_adet", "talep_tarihi", "onaylandi", "onay_tarihi")}),
        ("Gönderim Adresi", {"fields": ("farkli_adres_kullan", "il", "ilce", "adres_detay")}),
        ("Kargo", {"fields": ("kargolandimi", "kargo_tarihi", "kargo_sirketi", "kargo_takip_no")}),
    )
    readonly_fields = ("talep_tarihi", "onay_tarihi", "kargo_tarihi")

    @admin.action(description="Seçilen siparişleri ONAYLA")
    def isaretle_onaylandi(self, request, queryset):
        updated = queryset.update(onaylandi=True, onay_tarihi=timezone.now())
        self.message_user(request, f"{updated} sipariş onaylandı.", level=messages.SUCCESS)

    @admin.action(description="Seçilen siparişleri KARGOLANDI işaretle")
    def isaretle_kargolandı(self, request, queryset):
        updated = queryset.update(kargolandimi=True, kargo_tarihi=timezone.now())
        self.message_user(request, f"{updated} sipariş kargolandı olarak işaretlendi.", level=messages.SUCCESS)
