# veteriner/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Veteriner, SiparisIstemi
from .forms import VeterinerProfileForm, SiparisForm
from anahtarlik.models import Etiket, KANAL_VET

@login_required
def veteriner_profil_tamamla(request):
    vet, _ = Veteriner.objects.get_or_create(
        kullanici=request.user,
        defaults={"ad": request.user.get_full_name() or request.user.username, "aktif": True},
    )
    if vet.il and vet.adres_detay:
        return redirect("veteriner:veteriner_paneli")

    if request.method == "POST":
        form = VeterinerProfileForm(request.POST, instance=vet)
        if form.is_valid():
            form.save()
            messages.success(request, "Profiliniz güncellendi.")
            return redirect("veteriner:veteriner_paneli")
    else:
        form = VeterinerProfileForm(instance=vet)

    return render(request, "veteriner/profil_tamamla.html", {"form": form})

@login_required
def veteriner_paneli(request):
    vet = getattr(request.user, 'veteriner_profili', None)
    if vet is None or not vet.il or not vet.adres_detay:
        messages.info(request, "Lütfen veteriner profilinizi tamamlayın.")
        return redirect("veteriner:veteriner_profil_tamamla")

    if request.method == 'POST':
        siparis_form = SiparisForm(request.POST)
        if siparis_form.is_valid():
            siparis = siparis_form.save(commit=False)
            siparis.veteriner = vet
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

    tahsis_qs = Etiket.objects.filter(satici_veteriner=vet, kanal=KANAL_VET).order_by("-tahsis_tarihi", "-olusturulma_tarihi")
    satilan_qs = tahsis_qs.filter(aktif=True)
    siparis_qs = SiparisIstemi.objects.filter(veteriner=vet).order_by('-talep_tarihi')

    context = {
        "vet": vet,
        "tahsis_sayisi": tahsis_qs.count(),
        "satis_sayisi": satilan_qs.count(),
        "kalan_envanter": vet.kalan_envanter,  # ✅ yeni kart için
        "tahsis_edilenler": tahsis_qs[:5],
        "satilanlar": satilan_qs[:5],
        "siparis_istekleri": siparis_qs[:5],
        "siparis_form": siparis_form,
    }
    return render(request, "veteriner/panel.html", context)

# ---- Hepsini gör sayfaları ----

@login_required
def tahsis_listesi(request):
    vet = getattr(request.user, 'veteriner_profili', None)
    if vet is None or not vet.il or not vet.adres_detay:
        return redirect("veteriner:veteriner_profil_tamamla")

    qs = Etiket.objects.filter(satici_veteriner=vet, kanal=KANAL_VET).order_by("-tahsis_tarihi", "-olusturulma_tarihi")
    paginator = Paginator(qs, 25)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "veteriner/liste_tahsis.html", {"page_obj": page_obj})

@login_required
def satis_listesi(request):
    vet = getattr(request.user, 'veteriner_profili', None)
    if vet is None or not vet.il or not vet.adres_detay:
        return redirect("veteriner:veteriner_profil_tamamla")

    qs = Etiket.objects.filter(satici_veteriner=vet, kanal=KANAL_VET, aktif=True).order_by("-first_activated_at", "-aktiflestirme_tarihi")
    paginator = Paginator(qs, 25)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "veteriner/liste_satis.html", {"page_obj": page_obj})

@login_required
def siparis_listesi(request):
    vet = getattr(request.user, 'veteriner_profili', None)
    if vet is None or not vet.il or not vet.adres_detay:
        return redirect("veteriner:veteriner_profil_tamamla")

    qs = SiparisIstemi.objects.filter(veteriner=vet).order_by('-talep_tarihi')
    paginator = Paginator(qs, 25)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "veteriner/liste_siparis.html", {"page_obj": page_obj})
