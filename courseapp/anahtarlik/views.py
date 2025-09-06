# anahtarlik/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from .models import Sahip, EvcilHayvan, Etiket, SaglikKaydi, BeslenmeKaydi, Alerji, AsiTakvimi, IlacKaydi, AmeliyatKaydi, KiloKaydi
from .forms import EtiketForm, EvcilHayvanForm

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.urls import reverse  # <-- eklendi


@login_required
def profil_duzenle(request):
    sahip = get_object_or_404(Sahip, kullanici=request.user)
    if request.method == 'POST':
        sahip.ad = request.POST.get('ad')
        sahip.soyad = request.POST.get('soyad')
        sahip.telefon = request.POST.get('telefon')
        sahip.yedek_telefon = request.POST.get('yedek_telefon')
        sahip.acil_durum_kontagi = request.POST.get('acil_durum_kontagi')
        sahip.save()
        messages.success(request, "Profil bilgileri güncellendi.")
        return redirect('kullanici_paneli')
    return render(request, 'anahtarlik/profil_duzenle.html', {'sahip': sahip})


@login_required
def hayvan_pdf_indir(request, pet_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=pet_id, sahip__kullanici=request.user)
    template = get_template("anahtarlik/pdf_template.html")
    html = template.render({"hayvan": evcil_hayvan})

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="{evcil_hayvan.ad}_rapor.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response


import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def pet_detail(request, pet_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=pet_id, sahip__kullanici=request.user)

    asi_takvimi = evcil_hayvan.asi_takvimi.all().order_by('-planlanan_tarih')
    saglik_kayitlari = evcil_hayvan.saglik_kayitlari.all().order_by('-asi_tarihi')
    ilac_kayitlari = evcil_hayvan.ilac_kayitlari.all().order_by('-baslangic_tarihi')
    ameliyat_kayitlari = evcil_hayvan.ameliyat_kayitlari.all().order_by('-tarih')
    alerjiler = evcil_hayvan.alerjiler.all().order_by('-kaydedilme_tarihi')
    beslenme_kayitlari = evcil_hayvan.beslenme_kayitlari.all().order_by('-tarih')
    kilo_kayitlari = evcil_hayvan.kilo_kayitlari.all().order_by('tarih')

    # ✅ JSON’a çevir
    kilo_data = list(kilo_kayitlari.values("tarih", "kilo"))
    kilo_data_json = json.dumps(kilo_data, cls=DjangoJSONEncoder)

    context = {
        'hayvan': evcil_hayvan,
        'asi_takvimi': asi_takvimi,
        'saglik_kayitlari': saglik_kayitlari,
        'ilac_kayitlari': ilac_kayitlari,
        'ameliyat_kayitlari': ameliyat_kayitlari,
        'alerjiler': alerjiler,
        'beslenme_kayitlari': beslenme_kayitlari,
        'kilo_kayitlari': kilo_kayitlari,
        'kilo_data_json': kilo_data_json,   # ✅ Template’e JSON gönderiyoruz
    }
    return render(request, 'anahtarlik/pet_detail.html', context)


def ev(request):
    return render(request, 'anahtarlik/ev.html')

@login_required
def kullanici_paneli(request):
    sahip = get_object_or_404(Sahip, kullanici=request.user)
    evcil_hayvanlar = sahip.evcil_hayvanlar.all().order_by('-id')
    paginator = Paginator(evcil_hayvanlar, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'anahtarlik/kullanici_paneli.html', {'evcil_hayvanlar': page_obj})

@login_required
def add_pet(request):
    step = request.session.get('add_pet_step', 1)

    if step == 1:
        if request.method == 'POST':
            form = EtiketForm(request.POST)
            if form.is_valid():
                seri = form.cleaned_data['seri_numarasi']
                try:
                    etiket = Etiket.objects.get(seri_numarasi=seri)
                    if etiket.aktif:
                        messages.error(request, "Bu etiket zaten aktif!")
                    else:
                        request.session['etiket_id'] = etiket.id
                        request.session['add_pet_step'] = 2
                        return redirect('add_pet')
                except Etiket.DoesNotExist:
                    messages.error(request, "Bu seri numarası sistemde bulunamadı.")
        else:
            form = EtiketForm()
        return render(request, 'anahtarlik/add_pet.html', {'form': form, 'step': 1})

    elif step == 2:
        if 'etiket_id' not in request.session:
            return redirect('add_pet')

        if request.method == 'POST':
            form = EvcilHayvanForm(request.POST, request.FILES)
            if form.is_valid():
                with transaction.atomic():
                    sahip = get_object_or_404(Sahip, kullanici=request.user)
                    evcil = form.save(commit=False)
                    evcil.sahip = sahip
                    evcil.save()

                    etiket = Etiket.objects.get(id=request.session['etiket_id'])
                    etiket.evcil_hayvan = evcil
                    etiket.aktif = True
                    # ✅ QR URL'i reverse ile doğru üret
                    etiket.qr_kod_url = f"{settings.SITE_URL}{reverse('etiket:qr_landing', kwargs={'tag_id': etiket.etiket_id})}"
                    etiket.save()

                    del request.session['add_pet_step']
                    del request.session['etiket_id']

                    messages.success(request, 'Yeni evcil hayvan eklendi!')
                    return redirect('kullanici_paneli')
            else:
                print("Form geçersiz:", form.errors)
        else:
            form = EvcilHayvanForm()
        return render(request, 'anahtarlik/add_pet.html', {'form': form, 'step': 2})

    request.session['add_pet_step'] = 1
    return redirect('add_pet')


@login_required
def kayip_bildir(request, evcil_hayvan_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=evcil_hayvan_id, sahip__kullanici=request.user)
    if request.method == 'POST':
        evcil_hayvan.kayip_durumu = True
        evcil_hayvan.odul_miktari = request.POST.get('odul_miktari')
        evcil_hayvan.kayip_bildirim_tarihi = timezone.now()
        evcil_hayvan.save()
        messages.success(request, 'Kayıp bildirimi yapıldı!')
        return redirect('kullanici_paneli')
    return render(request, 'anahtarlik/kayip_bildir.html', {'evcil_hayvan': evcil_hayvan})

def hayvan_bulundu(request, evcil_hayvan_id):
    hayvan = get_object_or_404(EvcilHayvan, id=evcil_hayvan_id)
    
    if hayvan.kayip_durumu:
        hayvan.kayip_durumu = False
        hayvan.kayip_bildirim_tarihi = None
        hayvan.save()
        messages.success(request, f"{hayvan.ad} artık güvende olarak işaretlendi.")
    else:
        messages.info(request, f"{hayvan.ad} zaten kayıp değil.")
    
    return redirect("pet_detail", pet_id=hayvan.id)



@login_required
def edit_pet(request, pet_id):
    hayvan = get_object_or_404(EvcilHayvan, id=pet_id, sahip__kullanici=request.user)
    if request.method == 'POST':
        form = EvcilHayvanForm(request.POST, instance=hayvan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evcil hayvan bilgileri güncellendi!')
            return redirect('kullanici_paneli')
    else:
        form = EvcilHayvanForm(instance=hayvan)
    return render(request, 'anahtarlik/edit_pet.html', {'form': form, 'hayvan': hayvan})

@login_required
def delete_pet(request, pet_id):
    hayvan = get_object_or_404(EvcilHayvan, id=pet_id, sahip__kullanici=request.user)
    if request.method == 'POST':
        hayvan.delete()
        messages.success(request, 'Evcil hayvan silindi!')
        return redirect('kullanici_paneli')
    return render(request, 'anahtarlik/delete_confirm.html', {'hayvan': hayvan})
