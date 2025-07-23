# anahtarlik/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Sahip, EvcilHayvan, Etiket, Alerji, SaglikKaydi, AsiTakvimi,
    IlacKaydi, AmeliyatKaydi, BeslenmeKaydi, KiloKaydi
)

# Inline Modeller (İlişkili kayıtları aynı sayfada düzenleme için)
class AlerjiInline(admin.TabularInline):
    model = Alerji
    extra = 1  # Varsayılan olarak 1 boş form göster
    fields = ('alerji_turu', 'aciklama', 'kaydedilme_tarihi')
    readonly_fields = ('kaydedilme_tarihi',)

class SaglikKaydiInline(admin.TabularInline):
    model = SaglikKaydi
    extra = 1
    fields = ('asi_turu', 'asi_tarihi', 'notlar')

class AsiTakvimiInline(admin.TabularInline):
    model = AsiTakvimi
    extra = 1
    fields = ('asi_turu', 'planlanan_tarih', 'tamamlandi', 'tamamlanma_tarihi', 'notlar')

class IlacKaydiInline(admin.TabularInline):
    model = IlacKaydi
    extra = 1
    fields = ('ilac_adi', 'baslangic_tarihi', 'bitis_tarihi', 'dozaj', 'notlar')

class AmeliyatKaydiInline(admin.TabularInline):
    model = AmeliyatKaydi
    extra = 1
    fields = ('ameliyat_turu', 'tarih', 'veteriner', 'notlar')

class BeslenmeKaydiInline(admin.TabularInline):
    model = BeslenmeKaydi
    extra = 1
    fields = ('besin_turu', 'tarih', 'miktar', 'notlar')

class KiloKaydiInline(admin.TabularInline):
    model = KiloKaydi
    extra = 1
    fields = ('kilo', 'tarih', 'notlar')

# Sahip Admin
@admin.register(Sahip)
class SahipAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'ad', 'soyad', 'telefon', 'adres')
    search_fields = ('kullanici__username', 'ad', 'soyad', 'telefon')
    list_filter = ('kullanici__is_active',)
    readonly_fields = ('kullanici',)

# EvcilHayvan Admin (Ana model, inlines ile zenginleştirildi)
@admin.register(EvcilHayvan)
class EvcilHayvanAdmin(admin.ModelAdmin):
    list_display = ('ad', 'tur', 'cins', 'sahip', 'kayip_durumu_colored', 'resim_preview')
    search_fields = ('ad', 'cins', 'sahip__kullanici__username')
    list_filter = ('tur', 'kayip_durumu', 'cinsiyet')
    inlines = [
        AlerjiInline, SaglikKaydiInline, AsiTakvimiInline,
        IlacKaydiInline, AmeliyatKaydiInline, BeslenmeKaydiInline, KiloKaydiInline
    ]
    fieldsets = (
        ('Genel Bilgiler', {
            'fields': ('ad', 'tur', 'cins', 'cinsiyet', 'dogum_tarihi', 'sahip', 'resim', 'resim_preview')
        }),
        ('Ek Bilgiler', {
            'fields': ('saglik_notu', 'beslenme_notu','genel_not' ,'davranis_notu') 
        }),
        ('Kayıp Durumu', {
            'fields': ('kayip_durumu', 'kayip_bildirim_tarihi', 'odul_miktari')
        }),
    )
    readonly_fields = ('kayip_bildirim_tarihi', 'resim_preview')

    def kayip_durumu_colored(self, obj):
        color = 'red' if obj.kayip_durumu else 'green'
        return format_html('<span style="color: {};">{}</span>', color, 'Kayıp' if obj.kayip_durumu else 'Güvende')
    kayip_durumu_colored.short_description = 'Kayıp Durumu'

    def resim_preview(self, obj):
        if obj.resim:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 50%;" />',
                obj.resim.url
            )
        return 'Resim Yok'
    resim_preview.short_description = 'Resim Önizleme'

# Etiket Admin
@admin.register(Etiket)
class EtiketAdmin(admin.ModelAdmin):
    list_display = ('seri_numarasi', 'evcil_hayvan', 'aktif', 'qr_kod_url_link', 'olusturulma_tarihi')
    search_fields = ('seri_numarasi', 'evcil_hayvan__ad')
    list_filter = ('aktif', 'kilitli')
    readonly_fields = ('etiket_id', 'olusturulma_tarihi')

    def qr_kod_url_link(self, obj):
        if obj.qr_kod_url:
            return format_html('<a href="{}" target="_blank">QR Kod Linki</a>', obj.qr_kod_url)
        return 'Yok'
    qr_kod_url_link.short_description = 'QR Kod URL'

# Diğer Modeller (Basit register)
@admin.register(Alerji)
class AlerjiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'alerji_turu', 'kaydedilme_tarihi')
    search_fields = ('evcil_hayvan__ad', 'alerji_turu')
    list_filter = ('kaydedilme_tarihi',)

@admin.register(SaglikKaydi)
class SaglikKaydiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'asi_turu', 'asi_tarihi')
    search_fields = ('evcil_hayvan__ad', 'asi_turu')
    list_filter = ('asi_tarihi',)

@admin.register(AsiTakvimi)
class AsiTakvimiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'asi_turu', 'planlanan_tarih', 'tamamlandi')
    search_fields = ('evcil_hayvan__ad', 'asi_turu')
    list_filter = ('tamamlandi', 'planlanan_tarih')

@admin.register(IlacKaydi)
class IlacKaydiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'ilac_adi', 'baslangic_tarihi', 'bitis_tarihi')
    search_fields = ('evcil_hayvan__ad', 'ilac_adi')
    list_filter = ('baslangic_tarihi',)

@admin.register(AmeliyatKaydi)
class AmeliyatKaydiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'ameliyat_turu', 'tarih')
    search_fields = ('evcil_hayvan__ad', 'ameliyat_turu')
    list_filter = ('tarih',)

@admin.register(BeslenmeKaydi)
class BeslenmeKaydiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'besin_turu', 'tarih', 'miktar')
    search_fields = ('evcil_hayvan__ad', 'besin_turu')
    list_filter = ('tarih',)

@admin.register(KiloKaydi)
class KiloKaydiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'kilo', 'tarih')
    search_fields = ('evcil_hayvan__ad',)
    list_filter = ('tarih',)