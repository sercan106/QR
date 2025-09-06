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

    form = VeterinerProfileForm(request.POST or None, instance=vet)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profiliniz güncellendi.")
        return redirect("veteriner:veteriner_paneli")
    return render(request, "veteriner/profil_tamamla.html", {"form": form})

@login_required
def veteriner_paneli(request):
    vet = getattr(request.user, 'veteriner_profili', None)
    if vet is None or not vet.il or not vet.adres_detay:
        messages.info(request, "Lütfen veteriner profilinizi tamamlayın.")
        return redirect("veteriner:veteriner_profil_tamamla")

    # ✅ Sadece sipariş formu (adet + adres)
    if request.method == 'POST':
        form = SiparisForm(request.POST)
        if form.is_valid():
            siparis = form.save(commit=False)
            siparis.veteriner = vet
            # adres: farkli_adres_kullan False ise veterinerin kayıtlı adresini kullan
            if not siparis.farkli_adres_kullan:
                siparis.il = vet.il
                siparis.ilce = vet.ilce
                siparis.adres_detay = vet.adres_detay
            siparis.save()
            messages.success(request, "Sipariş talebiniz alındı.")
            return redirect('veteriner:veteriner_paneli')
    else:
        form = SiparisForm()

    tahsis_qs = Etiket.objects.filter(satici_veteriner=vet, kanal=KANAL_VET).order_by("-tahsis_tarihi", "-olusturulma_tarihi")
    satilan_qs = tahsis_qs.filter(aktif=True)
    siparis_qs = SiparisIstemi.objects.filter(veteriner=vet).order_by('-talep_tarihi')

    context = {
        "vet": vet,
        "tahsis_sayisi": tahsis_qs.count(),
        "satis_sayisi": satilan_qs.count(),
        "kalan_envanter": vet.kalan_envanter,
        "tahsis_edilenler": tahsis_qs[:5],
        "satilanlar": satilan_qs[:5],
        "siparis_istekleri": siparis_qs[:5],
        "siparis_form": form,
    }
    return render(request, "veteriner/panel.html", context)

@login_required
def tahsis_listesi(request):
    vet = getattr(request.user, 'veteriner_profili', None)
    if vet is None or not vet.il or not vet.adres_detay:
        return redirect("veteriner:veteriner_profil_tamamla")
    qs = Etiket.objects.filter(satici_veteriner=vet, kanal=KANAL_VET).order_by("-tahsis_tarihi", "-olusturulma_tarihi")
    page_obj = Paginator(qs, 25).get_page(request.GET.get("page"))
    return render(request, "veteriner/liste_tahsis.html", {"page_obj": page_obj})

@login_required
def satis_listesi(request):
    vet = getattr(request.user, 'veteriner_profili', None)
    if vet is None or not vet.il or not vet.adres_detay:
        return redirect("veteriner:veteriner_profil_tamamla")
    qs = Etiket.objects.filter(satici_veteriner=vet, kanal=KANAL_VET, aktif=True).order_by("-first_activated_at", "-aktiflestirme_tarihi")
    page_obj = Paginator(qs, 25).get_page(request.GET.get("page"))
    return render(request, "veteriner/liste_satis.html", {"page_obj": page_obj})

@login_required
def siparis_listesi(request):
    vet = getattr(request.user, 'veteriner_profili', None)
    if vet is None or not vet.il or not vet.adres_detay:
        return redirect("veteriner:veteriner_profil_tamamla")
    qs = SiparisIstemi.objects.filter(veteriner=vet).order_by('-talep_tarihi')
    page_obj = Paginator(qs, 25).get_page(request.GET.get("page"))
    return render(request, "veteriner/liste_siparis.html", {"page_obj": page_obj})
