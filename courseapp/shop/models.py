# shop/models.py
from django.db import models
from django.contrib.auth.models import User
from anahtarlik.models import EvcilHayvan

class Kategori(models.Model):
    ad = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.ad

class Urun(models.Model):
    ad = models.CharField(max_length=200)
    kisa_aciklama = models.CharField(max_length=200, blank=True, null=True)  # Yeni alan
    aciklama = models.TextField()
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    indirimli_fiyat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Yeni alan
    stok = models.IntegerField(default=0)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    tavsiye_edilen_tur = models.CharField(max_length=20, choices=EvcilHayvan.TUR_SECENEKLERI, blank=True)

    def __str__(self):
        return self.ad

    @property
    def indirim_orani(self):
        if self.indirimli_fiyat and self.fiyat:
            return ((self.fiyat - self.indirimli_fiyat) / self.fiyat * 100).quantize(models.Decimal('1'))
        return 0

class UrunResim(models.Model):
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE, related_name='resimler')
    resim = models.ImageField(upload_to='urunler/', null=True, blank=True)

    def __str__(self):
        return f"{self.urun.ad} - Resim"

class Siparis(models.Model):
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    toplam_fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    durum = models.CharField(max_length=20, choices=[('bekliyor', 'Bekliyor'), ('odendi', 'Ödendi'), ('gonderildi', 'Gönderildi')], default='bekliyor')
    adres = models.TextField()

    def __str__(self):
        return f"Sipariş {self.id} - {self.kullanici.username}"

class SiparisKalemi(models.Model):
    siparis = models.ForeignKey(Siparis, on_delete=models.CASCADE, related_name='kalemler')
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE)
    miktar = models.IntegerField(default=1)
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.miktar} x {self.urun.ad}"