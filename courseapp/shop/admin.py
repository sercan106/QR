# shop/admin.py (Modeller Türkçe, admin arayüzü özelleştirildi, birden fazla resim inline destekli)

from django.contrib import admin
from .models import Kategori, Urun, UrunResim, Siparis, SiparisKalemi

# Inline için UrunResim (birden fazla resim ekleme)
class UrunResimInline(admin.TabularInline):
    model = UrunResim
    extra = 1  # Varsayılan 1 boş form göster
    fields = ('resim',)  # Sadece resim alanı

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('ad', 'slug')  # Listede gösterilecek alanlar
    search_fields = ('ad',)  # Arama için
    prepopulated_fields = {'slug': ('ad',)}  # Slug otomatik doldur

@admin.register(Urun)
class UrunAdmin(admin.ModelAdmin):
    list_display = ('ad', 'fiyat', 'stok', 'kategori', 'tavsiye_edilen_tur')  # Listede göster
    search_fields = ('ad', 'aciklama')  # Arama
    list_filter = ('kategori', 'tavsiye_edilen_tur')  # Filtre
    inlines = [UrunResimInline]  # Birden fazla resim ekleme inline

@admin.register(Siparis)
class SiparisAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'olusturulma_tarihi', 'toplam_fiyat', 'durum')  # Listede göster
    search_fields = ('kullanici__username',)  # Arama
    list_filter = ('durum', 'olusturulma_tarihi')  # Filtre

# Inline için SiparisKalemi (sipariş kalemleri)
class SiparisKalemiInline(admin.TabularInline):
    model = SiparisKalemi
    extra = 0  # Boş form yok
    fields = ('urun', 'miktar', 'fiyat')

# SiparisAdmin'e inline ekle (sipariş detaylarını göster)
SiparisAdmin.inlines = [SiparisKalemiInline]

@admin.register(SiparisKalemi)
class SiparisKalemiAdmin(admin.ModelAdmin):
    list_display = ('siparis', 'urun', 'miktar', 'fiyat')  # Listede göster
    search_fields = ('urun__ad',)  # Arama

@admin.register(UrunResim)
class UrunResimAdmin(admin.ModelAdmin):
    list_display = ('urun', 'resim')  # Listede göster
    search_fields = ('urun__ad',)  # Arama