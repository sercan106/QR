from django.db import models
from django.contrib.auth.models import User

# Yeni ödeme modeli sabitleri
ODEME_PESIN = 'PESIN'
ODEME_KONSINYE = 'KONSINYE'
ODEME_SECENEKLERI = [
    (ODEME_PESIN, 'Peşin Ödeme'),
    (ODEME_KONSINYE, 'Konsinye (Numune) Ödeme'),
]

class Veteriner(models.Model):
    ad = models.CharField(max_length=150)
    telefon = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    il = models.CharField(max_length=50, blank=True)
    ilce = models.CharField(max_length=50, blank=True)
    adres_detay = models.TextField(blank=True)

    kullanici = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='veteriner_profili')

    aktif = models.BooleanField(default=True)
    olusturulma = models.DateTimeField(auto_now_add=True)
    
    # --- YENİ ALAN ---
    odeme_modeli = models.CharField(max_length=10, choices=ODEME_SECENEKLERI, default=ODEME_PESIN)

    # Sayaçlar
    tahsis_sayisi = models.PositiveIntegerField(default=0)  # verilen etiket adedi (ilk tahsis)
    satis_sayisi  = models.PositiveIntegerField(default=0)  # ilk aktivasyon adedi

    class Meta:
        ordering = ['ad']
        verbose_name = 'Veteriner'
        verbose_name_plural = 'Veterinerler'

    def __str__(self):
        return self.ad