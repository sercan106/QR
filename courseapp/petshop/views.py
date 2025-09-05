# petshop/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Petshop
from .forms import PetshopProfileForm

@login_required
def petshop_profil_tamamla(request):
    shop, _created = Petshop.objects.get_or_create(
        kullanici=request.user,
        defaults={"ad": "", "aktif": True}
    )

    if request.method == "POST":
        form = PetshopProfileForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, "Profiliniz kaydedildi.")
            return redirect("kullanici_paneli")
    else:
        form = PetshopProfileForm(instance=shop)

    return render(request, "petshop/profil_tamamla.html", {"form": form})
