# veteriner/forms.py
from django import forms
from .models import Veteriner, SiparisIstemi

class VeterinerProfileForm(forms.ModelForm):
    class Meta:
        model = Veteriner
        fields = ["ad", "telefon", "email", "il", "ilce", "adres_detay", "odeme_modeli"]
        widgets = {
            "ad": forms.TextInput(attrs={"class": "form-control"}),
            "telefon": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "il": forms.TextInput(attrs={"class": "form-control"}),
            "ilce": forms.TextInput(attrs={"class": "form-control"}),
            "adres_detay": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "odeme_modeli": forms.Select(attrs={"class": "form-select"}),
        }

class SiparisForm(forms.ModelForm):
    class Meta:
        model = SiparisIstemi
        # ❗ sadece adet + (opsiyonel) farklı adres
        fields = ["talep_edilen_adet", "farkli_adres_kullan", "il", "ilce", "adres_detay"]
        widgets = {
            "talep_edilen_adet": forms.NumberInput(attrs={"class": "form-control", "min": 5}),
            "farkli_adres_kullan": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "il": forms.TextInput(attrs={"class": "form-control"}),
            "ilce": forms.TextInput(attrs={"class": "form-control"}),
            "adres_detay": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("farkli_adres_kullan"):
            if not cleaned.get("il") or not cleaned.get("ilce") or not cleaned.get("adres_detay"):
                raise forms.ValidationError("Farklı adrese gönderim seçildi. İl / İlçe / Adres zorunlu.")
        return cleaned
