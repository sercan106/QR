# veteriner/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

# Ödeme modeli (kurum)
ODEME_PESIN = 'PESIN'
ODEME_KONSINYE = 'KONSINYE'
ODEME_SECENEKLERI = [
    (ODEME_PESIN, 'Peşin Ödeme'),
    (ODEME_KONSINYE, 'Konsinye (Numune) Ödeme'),
]

# Kargo şirketi
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

# Ödeme durumu (sipariş)
OD_BEKE = 'BEKLEMEDE'
OD_ALIN = 'ALINDI'
OD_IADE = 'IADE'
OD_MUAF = 'MUAF'  # Numune vb. için
ODEME_DURUM_SEC = [
    (OD_BEKE, 'Beklemede'),
    (OD_ALIN, 'Alındı'),
    (OD_IADE, 'İade Edildi'),
    (OD_MUAF, 'Muaf (Numune)'),
]

# Ödeme yöntemi
OY_NAKIT = 'NAKIT'
OY_EFT = 'EFT'
OY_KREDI = 'KREDI'
OY_POS = 'POS'
OY_DIGER = 'DIGER'
ODEME_YONTEM_SEC = [
    (OY_NAKIT, 'Nakit'),
    (OY_EFT, 'EFT/Havale'),
    (OY_KREDI, 'Kredi Kartı'),
    (OY_POS, 'Pos/Link'),
    (OY_DIGER, 'Diğer'),
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
    talep_edilen_adet = models.PositiveIntegerField(default=5, validators=[MinValueValidator(5)])
    talep_tarihi = models.DateTimeField(auto_now_add=True)

    # Onay/kargo
    onaylandi = models.BooleanField(default=False)
    onay_tarihi = models.DateTimeField(null=True, blank=True)
    kargolandimi = models.BooleanField(default=False)
    kargo_tarihi = models.DateTimeField(null=True, blank=True)
    kargo_sirketi = models.CharField(max_length=20, choices=KARGO_SECENEKLERI, blank=True)
    kargo_takip_no = models.CharField(max_length=100, blank=True)

    # Gönderim adresi
    farkli_adres_kullan = models.BooleanField(default=False)
    il = models.CharField(max_length=50, blank=True)
    ilce = models.CharField(max_length=50, blank=True)
    adres_detay = models.TextField(blank=True)

    # Numune / Ödeme takibi
    numune_mi = models.BooleanField(default=False)
    odeme_durumu = models.CharField(max_length=12, choices=ODEME_DURUM_SEC, default=OD_BEKE)
    odeme_tutari = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    odeme_para_birimi = models.CharField(max_length=6, default='TRY')
    odeme_yontemi = models.CharField(max_length=10, choices=ODEME_YONTEM_SEC, blank=True)
    odeme_alinma_tarihi = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.veteriner.ad} - {self.talep_edilen_adet} adet"

    @property
    def gonderim_adresi(self) -> str:
        if self.farkli_adres_kullan and self.il and self.ilce and self.adres_detay:
            return f"{self.adres_detay}, {self.ilce}/{self.il}"
        v = self.veteriner
        return f"{v.adres_detay}, {v.ilce}/{v.il}".strip(", /")

    @property
    def odeme_alindi_mi(self) -> bool:
        return self.odeme_durumu == OD_ALIN or (self.numune_mi and self.odeme_durumu == OD_MUAF)

    def save(self, *args, **kwargs):
        # Ödeme alındı ise tarih otomatİk set
        if self.odeme_durumu == OD_ALIN and not self.odeme_alinma_tarihi:
            self.odeme_alinma_tarihi = timezone.now()
        # Numunede ödeme muaf ise sıfırla
        if self.numune_mi and self.odeme_durumu == OD_MUAF:
            self.odeme_tutari = None
            self.odeme_yontemi = ''
            self.odeme_alinma_tarihi = None
        super().save(*args, **kwargs)
