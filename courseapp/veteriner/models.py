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

# Kargo şirketi örnek choices
KARGO_ARAS = 'ARAS'
KARGO_YURTICI = 'YURTICI'
KARGO_MNG = 'MNG'
KARGO_DHL = 'DHL'
KARGO_SECENEKLERI = [
    (KARGO_ARAS, 'Aras Kargo'),
    (KARGO_YURTICI, 'Yurtiçi Kargo'),
    (KARGO_MNG, 'MNG Kargo'),
    (KARGO_DHL, 'DHL'),
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

    # sayaçlar
    tahsis_sayisi = models.PositiveIntegerField(default=0)
    satis_sayisi = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.ad

    @property
    def kalan_envanter(self) -> int:
        return max((self.tahsis_sayisi or 0) - (self.satis_sayisi or 0), 0)


class SiparisIstemi(models.Model):
    veteriner = models.ForeignKey(Veteriner, on_delete=models.CASCADE, related_name='siparis_istekleri')

    # iş kuralı: min 5
    talep_edilen_adet = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(5)]
    )

    talep_tarihi = models.DateTimeField(auto_now_add=True)
    onaylandi = models.BooleanField(default=False)
    onay_tarihi = models.DateTimeField(null=True, blank=True)

    # farklı adrese gönderim
    farkli_adres_kullan = models.BooleanField(default=False)
    il = models.CharField(max_length=50, blank=True)
    ilce = models.CharField(max_length=50, blank=True)
    adres_detay = models.TextField(blank=True)

    # 🚚 Kargo alanları (admin takip için)
    kargo_sirketi = models.CharField(max_length=20, choices=KARGO_SECENEKLERI, blank=True)
    kargo_takip_no = models.CharField(max_length=100, blank=True)
    kargolandimi = models.BooleanField(default=False)
    kargo_tarihi = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.veteriner.ad} - {self.talep_edilen_adet} adet"

    @property
    def gonderim_adresi(self) -> str:
        if self.farkli_adres_kullan and self.il and self.ilce and self.adres_detay:
            return f"{self.adres_detay}, {self.ilce}/{self.il}"
        # aksi halde veterinerin adresi
        v = self.veteriner
        return f"{v.adres_detay}, {v.ilce}/{v.il}".strip(", /")
