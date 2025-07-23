# shop/forms.py (Form label'ları Türkçe)

from django import forms

class SiparisFormu(forms.Form):
    adres = forms.CharField(label="Teslimat Adresi", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))