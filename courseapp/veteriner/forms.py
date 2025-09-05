# veteriner/forms.py
from django import forms
from .models import Veteriner

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
