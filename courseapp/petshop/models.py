# petshop/models.py
from django.db import models
from django.contrib.auth.models import User

class Petshop(models.Model):
    ad = models.CharField(max_length=150)
    telefon = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    il = models.CharField(max_length=50, blank=True)
    ilce = models.CharField(max_length=50, blank=True)
    adres_detay = models.TextField(blank=True)

    kullanici = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='petshop_profili')

    aktif = models.BooleanField(default=True)
    olusturulma = models.DateTimeField(auto_now_add=True)

    # Sayaçlar
    tahsis_sayisi = models.PositiveIntegerField(default=0)
    satis_sayisi  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ad']
        verbose_name = 'Petshop'
        verbose_name_plural = 'Petshoplar'

    def __str__(self):
        return self.ad
