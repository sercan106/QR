# anahtarlik/forms.py

from django import forms
from .models import EvcilHayvan
from django.utils import timezone

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
    resim = forms.ImageField(
        label="Profil Görseli",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = EvcilHayvan
        fields = [
            'ad', 'tur', 'cins', 'cinsiyet', 'dogum_tarihi',
            'saglik_notu', 'beslenme_notu', 'genel_not', 'davranis_notu', 'resim'
        ]
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control'}),
            'cins': forms.TextInput(attrs={'class': 'form-control'}),
            'saglik_notu': forms.Textarea(attrs={'class': 'form-control form-textarea'}),
            'beslenme_notu': forms.Textarea(attrs={'class': 'form-control form-textarea'}),
            'genel_not': forms.Textarea(attrs={'class': 'form-control form-textarea'}),
            'davranis_notu': forms.Textarea(attrs={'class': 'form-control form-textarea'}),
        }

    def clean_dogum_tarihi(self):
        dogum_tarihi = self.cleaned_data.get('dogum_tarihi')
        if dogum_tarihi and dogum_tarihi > timezone.now().date():
            raise forms.ValidationError("Doğum tarihi gelecekte olamaz.")
        return dogum_tarihi
