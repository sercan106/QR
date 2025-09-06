# veteriner/admin.py

from django.contrib import admin, messages
from django.utils import timezone
from .models import (
    Veteriner,
    SiparisIstemi,
    OD_ALIN,
    OD_IADE,
    OD_MUAF,
)

# =========================
# VETERİNER ADMIN
# =========================

@admin.register(Veteriner)
class VeterinerAdmin(admin.ModelAdmin):
    list_display = (
        "ad", "il", "ilce", "telefon",
        "odeme_modeli", "tahsis_sayisi", "satis_sayisi",
        "kalan_envanter_goster", "aktif",
    )
    list_filter = ("aktif", "odeme_modeli", "il", "ilce")
    search_fields = ("ad", "telefon", "email", "il", "ilce")
    ordering = ("-olusturulma",)

    def kalan_envanter_goster(self, obj):
        return obj.kalan_envanter
    kalan_envanter_goster.short_description = "Kalan Envanter"


# =========================
# SİPARİŞ İSTEMİ ADMIN
# =========================

@admin.register(SiparisIstemi)
class SiparisIstemiAdmin(admin.ModelAdmin):
    # Liste görünümü
    list_display = (
        "veteriner", "talep_edilen_adet", "talep_tarihi",
        "numune_mi", "odeme_durumu", "odeme_alindi_mi_goster",
        "kargolandimi", "kargo_sirketi", "kargo_takip_no",
    )
    list_filter = (
        "onaylandi", "numune_mi", "odeme_durumu",
        "kargolandimi", "kargo_sirketi", "talep_tarihi",
    )
    search_fields = (
        "veteriner__ad", "veteriner__il", "veteriner__ilce",
        "kargo_takip_no", "il", "ilce", "adres_detay",
    )
    date_hierarchy = "talep_tarihi"
    ordering = ("-talep_tarihi",)

    # Form düzeni
    fieldsets = (
        ("Sipariş", {
            "fields": ("veteriner", "talep_edilen_adet", "talep_tarihi", "onaylandi", "onay_tarihi")
        }),
        ("Gönderim Adresi", {
            "fields": ("farkli_adres_kullan", "il", "ilce", "adres_detay")
        }),
        ("Numune / Ödeme", {
            "fields": ("numune_mi", "odeme_durumu", "odeme_tutari", "odeme_para_birimi", "odeme_yontemi", "odeme_alinma_tarihi")
        }),
        ("Kargo", {
            "fields": ("kargolandimi", "kargo_tarihi", "kargo_sirketi", "kargo_takip_no")
        }),
    )
    readonly_fields = ("talep_tarihi", "onay_tarihi", "kargo_tarihi", "odeme_alinma_tarihi")

    # Aksiyonlar
    actions = [
        "isaretle_onayla",
        "isaretle_odeme_alindi",
        "isaretle_odeme_iade",
        "isaretle_odeme_muaf",
        "isaretle_kargolandi",
    ]

    # ---- Yardımcı sütunlar ----
    def odeme_alindi_mi_goster(self, obj):
        return obj.odeme_alindi_mi
    odeme_alindi_mi_goster.boolean = True
    odeme_alindi_mi_goster.short_description = "Ödeme Alındı mı?"

    # ---- Kayıt kuralları (manuel kayıt/editleme) ----
    def save_model(self, request, obj, form, change):
        """
        Admin formundan kayıt/editleme yapılırken de iş kuralları uygulansın:
        - Ödeme alınmadan (ve numune değilken) kargo işaretlenemesin.
        - Ödeme ALINDI ise odeme_alinma_tarihi otomatik dolsun.
        """
        # Ödeme alındı ise tarih set et
        if obj.odeme_durumu == OD_ALIN and not obj.odeme_alinma_tarihi:
            obj.odeme_alinma_tarihi = timezone.now()

        # Numune değil ve ödeme ALINMADI ise kargo işaretlenemez
        if obj.kargolandimi and not obj.numune_mi and obj.odeme_durumu != OD_ALIN:
            self.message_user(
                request,
                "Ödeme alınmadan (ve numune değilken) kargo işaretlenemez.",
                level=messages.ERROR,
            )
            # Kargo alanlarını geri al
            obj.kargolandimi = False
            obj.kargo_tarihi = None

        super().save_model(request, obj, form, change)

    # ---- Aksiyonlar ----

    @admin.action(description="SİPARİŞ: Onayla")
    def isaretle_onayla(self, request, queryset):
        updated = queryset.update(onaylandi=True, onay_tarihi=timezone.now())
        self.message_user(request, f"{updated} sipariş ONAYLANDI.", level=messages.SUCCESS)

    @admin.action(description="ÖDEME: Alındı (tarih otomatik)")
    def isaretle_odeme_alindi(self, request, queryset):
        updated = 0
        for s in queryset:
            s.odeme_durumu = OD_ALIN
            if not s.odeme_alinma_tarihi:
                s.odeme_alinma_tarihi = timezone.now()
            s.save()
            updated += 1
        self.message_user(request, f"{updated} siparişte ÖDEME ALINDI.", level=messages.SUCCESS)

    @admin.action(description="ÖDEME: İade edildi")
    def isaretle_odeme_iade(self, request, queryset):
        updated = queryset.update(odeme_durumu=OD_IADE)
        self.message_user(request, f"{updated} siparişte ÖDEME İADE edildi.", level=messages.SUCCESS)

    @admin.action(description="ÖDEME: Muaf (Numune)")
    def isaretle_odeme_muaf(self, request, queryset):
        updated = 0
        for s in queryset:
            s.numune_mi = True
            s.odeme_durumu = OD_MUAF
            s.odeme_tutari = None
            s.odeme_yontemi = ""
            s.odeme_alinma_tarihi = None
            s.save()
            updated += 1
        self.message_user(request, f"{updated} sipariş ÖDEME MUAF (Numune) oldu.", level=messages.SUCCESS)

    @admin.action(description="KARGO: Kargolandı olarak işaretle (ödeme şart)")
    def isaretle_kargolandi(self, request, queryset):
        """
        Kargolama şu şartlarla izinli:
          - sipariş numune ise (odeme_durumu=MUAF) → OK
          - ya da ödeme ALINDI ise → OK
        Aksi halde atlanır ve uyarı verilir.
        """
        ok = 0
        skipped = 0
        for s in queryset:
            if s.numune_mi or s.odeme_durumu == OD_ALIN:
                s.kargolandimi = True
                if not s.kargo_tarihi:
                    s.kargo_tarihi = timezone.now()
                s.save()
                ok += 1
            else:
                skipped += 1

        if ok:
            self.message_user(
                request,
                f"{ok} sipariş KARGOLANDI olarak işaretlendi.",
                level=messages.SUCCESS
            )
        if skipped:
            self.message_user(
                request,
                f"{skipped} sipariş atlandı: ödeme alınmadı (ve numune değil).",
                level=messages.WARNING
            )
