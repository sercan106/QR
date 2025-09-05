# veteriner/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Veteriner
from .forms import VeterinerProfileForm

# Etiket modelini buradan import ediyoruz (ilişkili listelemeler için)
from anahtarlik.models import Etiket, KANAL_VET

# Veteriner yetkilendirme kontrolü için yardımcı fonksiyon
def is_veteriner(user):
    return hasattr(user, 'veteriner_profili')

@login_required
@user_passes_test(is_veteriner)
def veteriner_profil_tamamla(request):
    """
    Geçici kullanıcı adı/şifre ile giren veteriner,
    eksik profilini tamamlar. Tamamsa direkt panel'e atar.
    """
    vet, created = Veteriner.objects.get_or_create(
        kullanici=request.user,
        defaults={"ad": request.user.get_full_name() or request.user.username, "aktif": True},
    )

    # Zaten tamamlanmışsa panel'e gönder
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
@user_passes_test(is_veteriner)
def veteriner_paneli(request):
    """
    Veteriner ana paneli:
    - Tahsis edilen etiketler
    - Satılan (ilk aktivasyonu yapılmış) etiketler
    - Sayaçların özet görünümü
    """
    try:
        vet = request.user.veteriner_profili
    except Veteriner.DoesNotExist:
        messages.info(request, "Lütfen veteriner profilinizi tamamlayın.")
        return redirect("veteriner:veteriner_profil_tamamla")

    # Profil eksikse tamamlama sayfasına yönlendir
    if not vet.il or not vet.adres_detay:
        return redirect("veteriner:veteriner_profil_tamamla")

    tahsis_edilenler = Etiket.objects.filter(
        satici_veteriner=vet,
        kanal=KANAL_VET
    ).order_by("-tahsis_tarihi", "-olusturulma_tarihi")

    satilanlar = tahsis_edilenler.filter(aktif=True).order_by("-first_activated_at", "-aktiflestirme_tarihi")

    context = {
        "vet": vet,
        "tahsis_sayisi": vet.tahsis_sayisi,
        "satis_sayisi": vet.satis_sayisi,
        "tahsis_edilenler": tahsis_edilenler,
        "satilanlar": satilanlar,
    }
    return render(request, "veteriner/panel.html", context)