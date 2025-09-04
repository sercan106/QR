# etiket/forms.py
from django import forms

class SeriNumaraForm(forms.Form):
    seri_numarasi = forms.CharField(label="Etiket (Künye) Numarası", max_length=100)
