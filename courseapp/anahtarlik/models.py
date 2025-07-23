# anahtarlik/models.py


from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class Sahip(models.Model):
    kullanici = models.OneToOneField(User, on_delete=models.CASCADE)
    ad = models.CharField(max_length=50, blank=True)
    soyad = models.CharField(max_length=50, blank=True)
    telefon = models.CharField(max_length=15, blank=True)
    yedek_telefon = models.CharField(max_length=15, blank=True)
    adres = models.TextField(blank=True)
    acil_durum_kontagi = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.ad} {self.soyad}".strip() or self.kullanici.username

class EvcilHayvan(models.Model):
    TUR_SECENEKLERI = [
        ('kopek', 'Köpek'),
        ('kedi', 'Kedi'),
        ('diger', 'Diğer'),
    ]
    CINSIYET_SECENEKLERI = [
        ('erkek', 'Erkek'),
        ('disi', 'Dişi'),
        ('bilinmiyor', 'Bilinmiyor'),
    ]
    ad = models.CharField(max_length=100)
    tur = models.CharField(max_length=20, choices=TUR_SECENEKLERI)
    cins = models.CharField(max_length=100)
    cinsiyet = models.CharField(max_length=20, choices=CINSIYET_SECENEKLERI, default='bilinmiyor')
    dogum_tarihi = models.DateField(null=True, blank=True)
    sahip = models.ForeignKey(Sahip, on_delete=models.CASCADE, related_name='evcil_hayvanlar')
    saglik_notu = models.TextField(blank=True)
    beslenme_notu = models.TextField(blank=True)
    genel_not = models.TextField(blank=True)
    davranis_notu = models.TextField(blank=True)
    kayip_durumu = models.BooleanField(default=False)
    kayip_bildirim_tarihi = models.DateTimeField(null=True, blank=True)
    odul_miktari = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    resim = models.ImageField(upload_to='evcil_hayvanlar/', null=True, blank=True)

    def __str__(self):
        return f"{self.ad} ({self.get_tur_display()})"

class Etiket(models.Model):
    etiket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    seri_numarasi = models.CharField(max_length=50, unique=True)
    evcil_hayvan = models.OneToOneField(EvcilHayvan, on_delete=models.CASCADE, null=True, blank=True)
    qr_kod_url = models.URLField(blank=True)
    aktif = models.BooleanField(default=False)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    kilitli = models.BooleanField(default=False)

    def __str__(self):
        return f"Etiket {self.seri_numarasi} - {self.evcil_hayvan.ad if self.evcil_hayvan else 'Tanımlanmamış'}"

class Alerji(models.Model):
    evcil_hayvan = models.ForeignKey(EvcilHayvan, on_delete=models.CASCADE, related_name='alerjiler')
    alerji_turu = models.CharField(max_length=100)
    aciklama = models.TextField(blank=True)
    kaydedilme_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.evcil_hayvan.ad} - {self.alerji_turu}"

class SaglikKaydi(models.Model):
    evcil_hayvan = models.ForeignKey(EvcilHayvan, on_delete=models.CASCADE, related_name='saglik_kayitlari')
    asi_turu = models.CharField(max_length=100)
    asi_tarihi = models.DateField()
    notlar = models.TextField(blank=True)

    def __str__(self):
        return f"{self.evcil_hayvan.ad} - {self.asi_turu}"

class AsiTakvimi(models.Model):
    evcil_hayvan = models.ForeignKey(EvcilHayvan, on_delete=models.CASCADE, related_name='asi_takvimi')
    asi_turu = models.CharField(max_length=100)
    planlanan_tarih = models.DateField()
    tamamlandi = models.BooleanField(default=False)
    tamamlanma_tarihi = models.DateField(null=True, blank=True)
    notlar = models.TextField(blank=True)

    def __str__(self):
        return f"{self.evcil_hayvan.ad} - {self.asi_turu} (Plan: {self.planlanan_tarih})"

class IlacKaydi(models.Model):
    evcil_hayvan = models.ForeignKey(EvcilHayvan, on_delete=models.CASCADE, related_name='ilac_kayitlari')
    ilac_adi = models.CharField(max_length=100)
    baslangic_tarihi = models.DateField()
    bitis_tarihi = models.DateField(null=True, blank=True)
    dozaj = models.CharField(max_length=50, blank=True)
    notlar = models.TextField(blank=True)

    def __str__(self):
        return f"{self.evcil_hayvan.ad} - {self.ilac_adi}"

class AmeliyatKaydi(models.Model):
    evcil_hayvan = models.ForeignKey(EvcilHayvan, on_delete=models.CASCADE, related_name='ameliyat_kayitlari')
    ameliyat_turu = models.CharField(max_length=100)
    tarih = models.DateField()
    veteriner = models.CharField(max_length=100, blank=True)
    notlar = models.TextField(blank=True)

    def __str__(self):
        return f"{self.evcil_hayvan.ad} - {self.ameliyat_turu}"

class BeslenmeKaydi(models.Model):
    evcil_hayvan = models.ForeignKey(EvcilHayvan, on_delete=models.CASCADE, related_name='beslenme_kayitlari')
    besin_turu = models.CharField(max_length=100)
    tarih = models.DateField()
    miktar = models.CharField(max_length=50)
    notlar = models.TextField(blank=True)

    def __str__(self):
        return f"{self.evcil_hayvan.ad} - {self.besin_turu}"

class KiloKaydi(models.Model):
    evcil_hayvan = models.ForeignKey(EvcilHayvan, on_delete=models.CASCADE, related_name='kilo_kayitlari')
    kilo = models.DecimalField(max_digits=5, decimal_places=2)
    tarih = models.DateField()
    notlar = models.TextField(blank=True)

    def __str__(self):
        return f"{self.evcil_hayvan.ad} - {self.kilo} kg ({self.tarih})"