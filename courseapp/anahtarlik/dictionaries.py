from django.db import models


class Tur(models.Model):
    ad = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["ad"]

    def __str__(self):
        return self.ad


class Cins(models.Model):
    tur = models.ForeignKey(Tur, on_delete=models.CASCADE, related_name="cinsler")
    ad = models.CharField(max_length=120)

    class Meta:
        unique_together = ("tur", "ad")
        ordering = ["tur__ad", "ad"]

    def __str__(self):
        return f"{self.tur.ad} - {self.ad}"


class Il(models.Model):
    ad = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["ad"]

    def __str__(self):
        return self.ad


class Ilce(models.Model):
    il = models.ForeignKey(Il, on_delete=models.CASCADE, related_name="ilceler")
    ad = models.CharField(max_length=120)

    class Meta:
        unique_together = ("il", "ad")
        ordering = ["il__ad", "ad"]

    def __str__(self):
        return f"{self.ad} ({self.il.ad})"

