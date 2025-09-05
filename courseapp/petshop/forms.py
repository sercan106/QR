# petshop/forms.py
from django import forms
from .models import Petshop

class PetshopProfileForm(forms.ModelForm):
    class Meta:
        model = Petshop
        fields = ["ad", "telefon", "email", "il", "ilce", "adres_detay"]
        widgets = {
            "ad": forms.TextInput(attrs={"class": "form-control"}),
            "telefon": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "il": forms.TextInput(attrs={"class": "form-control"}),
            "ilce": forms.TextInput(attrs={"class": "form-control"}),
            "adres_detay": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
