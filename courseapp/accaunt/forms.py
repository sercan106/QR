# accaunt/forms.py (Register için özel, import hataları düzeltildi, fields kısıtlandı)

from django import forms
from django.contrib.auth.models import User
from anahtarlik.models import EvcilHayvan, Sahip
from django.utils import timezone  # Doğru import (datetime yerine django.utils)

class EtiketForm(forms.Form):
    seri_numarasi = forms.CharField(
        label="Etiket Seri Numarası",
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

class EvcilHayvanForm(forms.ModelForm):
    tur = forms.ChoiceField(
        choices=EvcilHayvan.TUR_SECENEKLERI,
        label="Tür",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cinsiyet = forms.ChoiceField(
        choices=EvcilHayvan.CINSIYET_SECENEKLERI,
        label="Cinsiyet",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    dogum_tarihi = forms.DateField(
        label="Doğum Tarihi",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )

    class Meta:
        model = EvcilHayvan
        fields = ['ad', 'tur', 'cins', 'cinsiyet', 'dogum_tarihi']  # Sadece istenen alanlar (saglik, beslenme, davranis kaldırıldı)
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control'}),
            'cins': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_dogum_tarihi(self):
        dogum_tarihi = self.cleaned_data.get('dogum_tarihi')
        if dogum_tarihi and dogum_tarihi > timezone.now().date():
            raise forms.ValidationError("Doğum tarihi gelecekte olamaz.")
        return dogum_tarihi

class KullaniciForm(forms.Form):
    ad = forms.CharField(
        max_length=50,
        label="Ad",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    soyad = forms.CharField(
        max_length=50,
        label="Soyad",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=150,
        label="Kullanıcı Adı",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="E-posta",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefon = forms.CharField(
        max_length=15,
        label="Telefon",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    yedek_telefon = forms.CharField(
        max_length=15,
        label="Yedek Telefon",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    adres = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control form-textarea'})
    )
    sifre = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Şifre"
    )
    sifre_tekrar = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Şifre (Tekrar)"
    )

    def clean(self):
        cleaned_data = super().clean()
        sifre = cleaned_data.get("sifre")
        sifre_tekrar = cleaned_data.get("sifre_tekrar")
        if sifre and sifre_tekrar and sifre != sifre_tekrar:
            raise forms.ValidationError("Şifreler eşleşmiyor.")
        return cleaned_data

    def clean_telefon(self):
        telefon = self.cleaned_data.get('telefon')
        if Sahip.objects.filter(telefon=telefon).exists():
            raise forms.ValidationError("Bu telefon numarası zaten kayıtlı.")
        return telefon

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu kullanıcı adı zaten kullanılıyor.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta zaten kayıtlı.")
        return email