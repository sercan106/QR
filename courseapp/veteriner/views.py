# veteriner/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Veteriner, SiparisIstemi
from .forms import VeterinerProfileForm, SiparisForm

# Etiket listesini göstermek ve sayıları hesaplamak için
from anahtarlik.models import Etiket, KANAL_VET


def is_veteriner(user) -> bool:
    """Kullanıcının veteriner profili var mı?"""
    return hasattr(user, 'veteriner_profili')


@login_required
def veteriner_profil_tamamla(request):
    """
    Profil yoksa oluşturur, varsa getirir.
    Zorunlu alanlar doluysa direkt panele yollar.
    (Decorators'tan user_passes_test kaldırıldı → self-onboarding kilidi kalktı)
    """
    vet, _ = Veteriner.objects.get_or_create(
        kullanici=request.user,
        defaults={"ad": request.user.get_full_name() or request.user.username, "aktif": True},
    )

    # Zaten tamamlanmışsa panele
    if vet.il and vet.adres_detay:
        return redirect("veteriner:veteriner_paneli")

    if request.method == "POST":
        form = VeterinerProfileForm(request.POST, instance=vet)
        if form.is_valid():
            form.save()
            messages.success(request, "Profiliniz başarıyla güncellendi.")
            return redirect("veteriner:veteriner_paneli")
    else:
        form = VeterinerProfileForm(instance=vet)

    return render(request, "veteriner/profil_tamamla.html", {"form": form})


@login_required
def veteriner_paneli(request):
    """
    Paneli sadece profili olan ve zorunlu alanları dolu veterinerler görür.
    Profil yoksa / eksikse 'profil/tamamla' sayfasına yönlendirir.
    """
    vet = getattr(request.user, 'veteriner_profili', None)
    if vet is None:
        messages.info(request, "Lütfen veteriner profilinizi tamamlayın.")
        return redirect("veteriner:veteriner_profil_tamamla")

    if not vet.il or not vet.adres_detay:
        return redirect("veteriner:veteriner_profil_tamamla")

    # Sipariş formu (POST)
    if request.method == 'POST':
        siparis_form = SiparisForm(request.POST)
        if siparis_form.is_valid():
            siparis = siparis_form.save(commit=False)
            siparis.veteriner = vet

            # Farklı adres işaretliyse formdan; değilse veterinerin kayıtlı adresinden al
            if siparis.farkli_adres_kullan:
                siparis.il = siparis_form.cleaned_data['il']
                siparis.ilce = siparis_form.cleaned_data['ilce']
                siparis.adres_detay = siparis_form.cleaned_data['adres_detay']
            else:
                siparis.il = vet.il
                siparis.ilce = vet.ilce
                siparis.adres_detay = vet.adres_detay

            siparis.save()
            messages.success(request, "Etiket sipariş talebiniz alındı.")
            return redirect('veteriner:veteriner_paneli')
    else:
        siparis_form = SiparisForm()

    # Tahsis edilenler (kanal=VET & bu veteriner)
    tahsis_edilenler = Etiket.objects.filter(
        satici_veteriner=vet,
        kanal=KANAL_VET
    ).order_by("-tahsis_tarihi", "-olusturulma_tarihi")

    # Satılan/Aktifleştirilenler
    satilanlar = tahsis_edilenler.filter(aktif=True)

    # Sipariş talepleri (en yeni üste)
    siparis_istekleri = SiparisIstemi.objects.filter(veteriner=vet).order_by('-talep_tarihi')

    context = {
        "vet": vet,
        "tahsis_sayisi": tahsis_edilenler.count(),
        "satis_sayisi": satilanlar.count(),
        "tahsis_edilenler": tahsis_edilenler[:5],
        "satilanlar": satilanlar[:5],
        "siparis_istekleri": siparis_istekleri,
        "siparis_form": siparis_form,
    }
    return render(request, "veteriner/panel.html", context)
