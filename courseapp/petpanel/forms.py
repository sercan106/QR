from django import forms
from anahtarlik.models import (
    EvcilHayvan, Sahip, Alerji, SaglikKaydi,
    IlacKaydi, AmeliyatKaydi, BeslenmeKaydi
)

# Alerji Formu
class AlerjiForm(forms.ModelForm):
    class Meta:
        model = Alerji
        fields = ['alerji_turu', 'aciklama']
        widgets = {
            'alerji_turu': forms.TextInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Sağlık Kaydı Formu
class SaglikForm(forms.ModelForm):
    class Meta:
        model = SaglikKaydi
        fields = ['asi_turu', 'asi_tarihi', 'notlar']
        widgets = {
            'asi_turu': forms.TextInput(attrs={'class': 'form-control'}),
            'asi_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notlar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# İlaç Kaydı Formu
class IlacForm(forms.ModelForm):
    class Meta:
        model = IlacKaydi
        fields = ['ilac_adi', 'baslangic_tarihi', 'bitis_tarihi', 'dozaj', 'notlar']
        widgets = {
            'ilac_adi': forms.TextInput(attrs={'class': 'form-control'}),
            'baslangic_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bitis_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dozaj': forms.TextInput(attrs={'class': 'form-control'}),
            'notlar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Ameliyat Kaydı Formu
class AmeliyatForm(forms.ModelForm):
    class Meta:
        model = AmeliyatKaydi
        fields = ['ameliyat_turu', 'tarih', 'veteriner', 'notlar']
        widgets = {
            'ameliyat_turu': forms.TextInput(attrs={'class': 'form-control'}),
            'tarih': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'veteriner': forms.TextInput(attrs={'class': 'form-control'}),
            'notlar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Beslenme Kaydı Formu
class BeslenmeForm(forms.ModelForm):
    class Meta:
        model = BeslenmeKaydi
        fields = ['besin_turu', 'tarih', 'miktar', 'notlar']
        widgets = {
            'besin_turu': forms.TextInput(attrs={'class': 'form-control'}),
            'tarih': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'miktar': forms.TextInput(attrs={'class': 'form-control'}),
            'notlar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Not Güncelleme Formu
class NotGuncellemeForm(forms.ModelForm):
    class Meta:
        model = EvcilHayvan
        fields = ['genel_not', 'davranis_notu', 'saglik_notu', 'beslenme_notu']
        widgets = {
            'genel_not': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'davranis_notu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'saglik_notu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'beslenme_notu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Evcil Hayvan Düzenleme Formu
class PetEditForm(forms.ModelForm):
    class Meta:
        model = EvcilHayvan
        fields = ['resim', 'ad', 'tur', 'cinsiyet', 'cins', 'dogum_tarihi']
        widgets = {
            'dogum_tarihi': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

# Sahip Bilgileri Formu
class SahipForm(forms.ModelForm):
    class Meta:
        model = Sahip
        fields = ['ad', 'soyad', 'telefon', 'yedek_telefon', 'acil_durum_kontagi', 'adres']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control'}),
            'soyad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control'}),
            'yedek_telefon': forms.TextInput(attrs={'class': 'form-control'}),
            'acil_durum_kontagi': forms.TextInput(attrs={'class': 'form-control'}),
            'adres': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
