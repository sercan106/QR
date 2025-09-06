# veteriner/forms.py

from django import forms
from .models import Veteriner, SiparisIstemi

class VeterinerProfileForm(forms.ModelForm):
    class Meta:
        model = Veteriner
        fields = ["ad", "telefon", "email", "il", "ilce", "adres_detay", "aktif"]
        widgets = {
            "ad": forms.TextInput(attrs={"class": "form-control"}),
            "telefon": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "il": forms.TextInput(attrs={"class": "form-control"}),
            "ilce": forms.TextInput(attrs={"class": "form-control"}),
            "adres_detay": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "aktif": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class SiparisForm(forms.ModelForm):
    # Yeni adres alanlarını ekliyoruz. Bunlar zorunlu değil.
    il = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    ilce = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    adres_detay = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)

    class Meta:
        model = SiparisIstemi
        fields = ['talep_edilen_adet', 'farkli_adres_kullan', 'il', 'ilce', 'adres_detay']
        widgets = {
            'talep_edilen_adet': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'farkli_adres_kullan': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        farkli_adres_kullan = cleaned_data.get('farkli_adres_kullan')
        
        # Eğer farklı adres seçilmişse, adres alanlarının doldurulmasını zorunlu kıl.
        if farkli_adres_kullan:
            if not cleaned_data.get('il'):
                self.add_error('il', 'İl alanı zorunludur.')
            if not cleaned_data.get('ilce'):
                self.add_error('ilce', 'İlçe alanı zorunludur.')
            if not cleaned_data.get('adres_detay'):
                self.add_error('adres_detay', 'Adres detay alanı zorunludur.')
        return cleaned_data