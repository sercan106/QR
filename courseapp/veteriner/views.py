# veteriner/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Veteriner, SiparisIstemi
from .forms import VeterinerProfileForm, SiparisForm

# Etiket modelini buradan import ediyoruz (ilişkili listelemeler için)
from anahtarlik.models import Etiket, KANAL_VET

# Veteriner yetkilendirme kontrolü için yardımcı fonksiyon
def is_veteriner(user):
    return hasattr(user, 'veteriner_profili')

@login_required
@user_passes_test(is_veteriner)
def veteriner_profil_tamamla(request):
    vet, created = Veteriner.objects.get_or_create(
        kullanici=request.user,
        defaults={"ad": request.user.get_full_name() or request.user.username, "aktif": True},
    )

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
    try:
        vet = request.user.veteriner_profili
    except Veteriner.DoesNotExist:
        messages.info(request, "Lütfen veteriner profilinizi tamamlayın.")
        return redirect("veteriner:veteriner_profil_tamamla")

    if not vet.il or not vet.adres_detay:
        return redirect("veteriner:veteriner_profil_tamamla")

    # POST isteği geldiğinde sipariş formunu işleriz
    if request.method == 'POST':
        siparis_form = SiparisForm(request.POST)
        if siparis_form.is_valid():
            siparis = siparis_form.save(commit=False)
            siparis.veteriner = vet
            siparis.save()
            messages.success(request, "Etiket sipariş talebiniz başarıyla alındı. En kısa sürede sizinle iletişime geçilecektir.")
            return redirect('veteriner:veteriner_paneli')
    else:
        siparis_form = SiparisForm()
        
    tahsis_edilenler = Etiket.objects.filter(
        satici_veteriner=vet,
        kanal=KANAL_VET
    ).order_by("-tahsis_tarihi", "-olusturulma_tarihi")

    satilanlar = tahsis_edilenler.filter(aktif=True)
    
    siparis_istekleri = SiparisIstemi.objects.filter(veteriner=vet).order_by('-talep_tarihi')

    context = {
        "vet": vet,
        "tahsis_sayisi": tahsis_edilenler.count(),
        "satis_sayisi": satilanlar.count(),
        "tahsis_edilenler": tahsis_edilenler[:5],
        "satilanlar": satilanlar[:5],
        "siparis_istekleri": siparis_istekleri,
        "siparis_form": siparis_form, # Formu bağlama dahil ediyoruz
    }
    return render(request, "veteriner/panel.html", context)