from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Petshop

@admin.register(Petshop)
class PetshopAdmin(admin.ModelAdmin):
    list_display = (
        'ad', 'il', 'ilce', 'telefon',
        'tahsis_sayisi', 'satis_sayisi',
        'aktif', 'olusturulma',
        'etiketler_link',
    )
    list_filter = ('aktif', 'il', 'ilce')
    search_fields = ('ad', 'telefon', 'email', 'il', 'ilce')
    readonly_fields = ('olusturulma', 'tahsis_sayisi', 'satis_sayisi')

    fieldsets = (
        ('Genel', {
            'fields': ('ad', 'telefon', 'email', 'aktif')
        }),
        ('Adres', {
            'fields': ('il', 'ilce', 'adres_detay')
        }),
        ('Sayaçlar', {
            'fields': ('tahsis_sayisi', 'satis_sayisi', 'olusturulma')
        }),
        ('Kullanıcı', {
            'fields': ('kullanici',),
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Admin yeni bir petshop eklerken otomatik olarak User oluşturur.
        """
        if not obj.kullanici:  # daha önce kullanıcı atanmadıysa
            username = f"shop_{obj.ad.lower().replace(' ', '_')}"
            temp_password = User.objects.make_random_password(length=8)
            user = User.objects.create(
                username=username,
                password=make_password(temp_password),
                is_active=True,
            )
            obj.kullanici = user

            self.message_user(
                request,
                f"Geçici kullanıcı oluşturuldu → Kullanıcı adı: {username}, Şifre: {temp_password}"
            )
        super().save_model(request, obj, form, change)

    def etiketler_link(self, obj):
        url = reverse('admin:anahtarlik_etiket_changelist')
        qs = f'?satici_petshop__id__exact={obj.id}'
        return format_html('<a href="{}{}">Etiketleri Gör</a>', url, qs)
    etiketler_link.short_description = 'Etiketler'
