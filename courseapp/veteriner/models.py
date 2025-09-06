# veteriner/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Ödeme modeli sabitleri
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

    kullanici = models.OneToOneField(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='veteriner_profili'
    )

    aktif = models.BooleanField(default=True)
    olusturulma = models.DateTimeField(auto_now_add=True)
    odeme_modeli = models.CharField(max_length=10, choices=ODEME_SECENEKLERI, default=ODEME_PESIN)

    # Sayaçlar (Etiket modeli bunları update eder)
    tahsis_sayisi = models.PositiveIntegerField(default=0)
    satis_sayisi = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.ad


class SiparisIstemi(models.Model):
    veteriner = models.ForeignKey(Veteriner, on_delete=models.CASCADE, related_name='siparis_istekleri')

    # Min 5 kuralıyla uyum için default=5 yaptık
    talep_edilen_adet = models.PositiveIntegerField(
        default=5,  # <-- DÜZELTİLDİ (önceden 1 idi)
        validators=[MinValueValidator(5)]
    )

    talep_tarihi = models.DateTimeField(auto_now_add=True)
    onaylandi = models.BooleanField(default=False)
    onay_tarihi = models.DateTimeField(null=True, blank=True)

    # Farklı adrese gönderim bilgileri
    farkli_adres_kullan = models.BooleanField(default=False)
    il = models.CharField(max_length=50, blank=True)
    ilce = models.CharField(max_length=50, blank=True)
    adres_detay = models.TextField(blank=True)

    def __str__(self):
        return f"{self.veteriner.ad} - {self.talep_edilen_adet} adet etiket siparişi"
