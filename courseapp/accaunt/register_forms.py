from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from anahtarlik.models import EvcilHayvan, Sahip
from anahtarlik.dictionaries import Tur, Cins, Il, Ilce


class EvcilHayvanKayitForm(forms.Form):
    ad = forms.CharField(label="Ad", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    tur = forms.ModelChoiceField(
        label="Tür",
        queryset=Tur.objects.all().order_by('ad'),
        required=True,
        empty_label="Seçiniz",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Cins seçiminde "Diğer" opsiyonu
    cins = forms.ChoiceField(
        label="Alt tür (Cins)", required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cins_diger = forms.CharField(label="Alt tür (Diğer)", required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Diğer alt tür'}))

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = self.data or self.initial
        try:
            tur_id = int(data.get('tur')) if data.get('tur') else None
        except ValueError:
            tur_id = None
        choices = [("", "Seçiniz")]
        if tur_id:
            choices += [(str(c.id), c.ad) for c in Cins.objects.filter(tur_id=tur_id).order_by('ad')]
        choices.append(("__OTHER__", "Diğer"))
        self.fields['cins'].choices = choices

    def clean(self):
        c = super().clean()
        if not c.get('tur'):
            self.add_error('tur', 'Lütfen tür seçin.')
        cins_val = c.get('cins')
        if not cins_val:
            self.add_error('cins', 'Lütfen alt tür seçin.')
        elif cins_val == '__OTHER__' and not c.get('cins_diger'):
            self.add_error('cins_diger', 'Diğer alt türü yazın.')
        dogum_tarihi = c.get('dogum_tarihi')
        if dogum_tarihi and dogum_tarihi > timezone.now().date():
            self.add_error('dogum_tarihi', "Doğum tarihi gelecekte olamaz.")
        return c


class KullaniciAdresForm(forms.Form):
    ad = forms.CharField(max_length=50, label="Ad", widget=forms.TextInput(attrs={'class': 'form-control'}))
    soyad = forms.CharField(max_length=50, label="Soyad", widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, label="Kullanıcı Adı", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-posta", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefon = forms.CharField(max_length=15, label="Telefon", widget=forms.TextInput(attrs={'class': 'form-control'}))
    yedek_telefon = forms.CharField(max_length=15, label="Yedek Telefon", widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    il = forms.ModelChoiceField(label="İl", queryset=Il.objects.all().order_by('ad'), required=True, empty_label="Seçiniz", widget=forms.Select(attrs={'class': 'form-control'}))
    ilce = forms.ModelChoiceField(label="İlçe", queryset=Ilce.objects.none(), required=True, empty_label="Seçiniz", widget=forms.Select(attrs={'class': 'form-control'}))
    adres = forms.CharField(label="Detaylı Adres", widget=forms.Textarea(attrs={'class': 'form-control form-textarea'}))

    sifre = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Şifre")
    sifre_tekrar = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Şifre (Tekrar)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = self.data or self.initial
        try:
            il_id = int(data.get('il')) if data.get('il') else None
        except ValueError:
            il_id = None
        if il_id:
            self.fields['ilce'].queryset = Ilce.objects.filter(il_id=il_id).order_by('ad')
        else:
            self.fields['ilce'].queryset = Ilce.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        sifre = cleaned_data.get("sifre")
        sifre_tekrar = cleaned_data.get("sifre_tekrar")
        if sifre and sifre_tekrar and sifre != sifre_tekrar:
            raise forms.ValidationError("Şifreler eşleşmiyor.")
        if not cleaned_data.get('il'):
            self.add_error('il', 'Lütfen bir il seçin.')
        if cleaned_data.get('il') and not cleaned_data.get('ilce'):
            self.add_error('ilce', 'Lütfen bir ilçe seçin.')
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
