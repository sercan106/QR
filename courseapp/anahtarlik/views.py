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




@login_required
def pet_detail(request, pet_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=pet_id, sahip__kullanici=request.user)

    asi_takvimi = evcil_hayvan.asi_takvimi.all().order_by('-planlanan_tarih')
    saglik_kayitlari = evcil_hayvan.saglik_kayitlari.all().order_by('-asi_tarihi')
    ilac_kayitlari = evcil_hayvan.ilac_kayitlari.all().order_by('-baslangic_tarihi')
    ameliyat_kayitlari = evcil_hayvan.ameliyat_kayitlari.all().order_by('-tarih')
    alerjiler = evcil_hayvan.alerjiler.all().order_by('-kaydedilme_tarihi')
    beslenme_kayitlari = evcil_hayvan.beslenme_kayitlari.all().order_by('-tarih')
    kilo_kayitlari = evcil_hayvan.kilo_kayitlari.all().order_by('-tarih')

    kayit_gruplari = [
        ("Aşı Takvimi", asi_takvimi, 'asi_takvimi_ekle', "🩺"),
        ("Sağlık Kayıtları", saglik_kayitlari, 'saglik_kaydi_ekle', "💉"),
        ("İlaç Kayıtları", ilac_kayitlari, 'ilac_kaydi_ekle', "💊"),
        ("Ameliyatlar", ameliyat_kayitlari, 'ameliyat_kaydi_ekle', "🏥"),
        ("Alerjiler", alerjiler, 'alerji_ekle', "⚠️"),
        ("Beslenme", beslenme_kayitlari, 'beslenme_kaydi_ekle', "🍗"),
        ("Kilo Takibi", kilo_kayitlari, 'kilo_kaydi_ekle', "⚖️"),
    ]

    context = {
        'hayvan': evcil_hayvan,
        'kayit_gruplari': kayit_gruplari,
    }
    return render(request, 'anahtarlik/pet_detail.html', context)






def ev(request):
    return render(request, 'anahtarlik/ev.html')

def tag(request):
    if request.method == 'POST':
        seri_numarasi = request.POST.get('seri_numarasi')
        try:
            etiket = Etiket.objects.get(seri_numarasi=seri_numarasi)
            if etiket.aktif:
                return redirect('etiket_goruntule', etiket_id=etiket.etiket_id)
            else:
                messages.error(request, 'Bu etiket henüz aktif değil!')
        except Etiket.DoesNotExist:
            messages.error(request, 'Geçersiz seri numarası!')
    return render(request, 'anahtarlik/tag.html')

def etiket_goruntule(request, etiket_id):
    etiket = get_object_or_404(Etiket, etiket_id=etiket_id)
    if not etiket.aktif:
        messages.error(request, 'Bu etiket aktif değil!')
        return redirect('ev')

    evcil_hayvan = etiket.evcil_hayvan
    sahip = evcil_hayvan.sahip

    if request.method == 'POST':
        mesaj = request.POST.get('mesaj')
        gonderen_ad = request.POST.get('gonderen_ad')
        send_mail(
            'Evcil Hayvanınız Bulundu!',
            f'{gonderen_ad} adlı kişi evcil hayvanınızı bulduğunu bildirdi:\n\n{mesaj}',
            'info@petsafehub.com',
            [sahip.kullanici.email],
            fail_silently=False,
        )
        messages.success(request, 'Mesaj sahibine gönderildi!')

    return render(request, 'anahtarlik/etiket_goruntule.html', {
        'etiket': etiket,
        'evcil_hayvan': evcil_hayvan,
        'sahip': sahip
    })

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
                    etiket.qr_kod_url = f"{settings.SITE_URL}/etiket/{etiket.etiket_id}"
                    etiket.save()

                    del request.session['add_pet_step']
                    del request.session['etiket_id']

                    messages.success(request, 'Yeni evcil hayvan eklendi!')
                    return redirect('kullanici_paneli')
            else:
                print("Form geçersiz:", form.errors)  # Terminale yaz
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

@login_required
def saglik_kaydi_ekle(request, evcil_hayvan_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=evcil_hayvan_id, sahip__kullanici=request.user)
    if request.method == 'POST':
        asi_turu = request.POST.get('asi_turu')
        asi_tarihi = request.POST.get('asi_tarihi')
        notlar = request.POST.get('notlar')
        SaglikKaydi.objects.create(
            evcil_hayvan=evcil_hayvan,
            asi_turu=asi_turu,
            asi_tarihi=asi_tarihi,
            notlar=notlar
        )
        messages.success(request, 'Sağlık kaydı eklendi!')
        return redirect('kullanici_paneli')
    return render(request, 'anahtarlik/saglik_kaydi_ekle.html', {'evcil_hayvan': evcil_hayvan})

@login_required
def beslenme_kaydi_ekle(request, evcil_hayvan_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=evcil_hayvan_id, sahip__kullanici=request.user)
    if request.method == 'POST':
        besin_turu = request.POST.get('besin_turu')
        tarih = request.POST.get('tarih')
        miktar = request.POST.get('miktar')
        notlar = request.POST.get('notlar')
        BeslenmeKaydi.objects.create(
            evcil_hayvan=evcil_hayvan,
            besin_turu=besin_turu,
            tarih=tarih,
            miktar=miktar,
            notlar=notlar
        )
        messages.success(request, 'Beslenme kaydı eklendi!')
        return redirect('kullanici_paneli')
    return render(request, 'anahtarlik/beslenme_kaydi_ekle.html', {'evcil_hayvan': evcil_hayvan})

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

@login_required
def alerji_ekle(request, evcil_hayvan_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=evcil_hayvan_id, sahip__kullanici=request.user)
    if request.method == 'POST':
        alerji_turu = request.POST.get('alerji_turu')
        aciklama = request.POST.get('aciklama')
        Alerji.objects.create(
            evcil_hayvan=evcil_hayvan,
            alerji_turu=alerji_turu,
            aciklama=aciklama
        )
        messages.success(request, 'Alerji kaydı eklendi!')
        return redirect('kullanici_paneli')
    return render(request, 'anahtarlik/alerji_ekle.html', {'evcil_hayvan': evcil_hayvan})

@login_required
def asi_takvimi_ekle(request, evcil_hayvan_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=evcil_hayvan_id, sahip__kullanici=request.user)
    if request.method == 'POST':
        asi_turu = request.POST.get('asi_turu')
        planlanan_tarih = request.POST.get('planlanan_tarih')
        tamamlandi = request.POST.get('tamamlandi') == 'on'
        tamamlanma_tarihi = request.POST.get('tamamlanma_tarihi') if tamamlandi else None
        notlar = request.POST.get('notlar')
        AsiTakvimi.objects.create(
            evcil_hayvan=evcil_hayvan,
            asi_turu=asi_turu,
            planlanan_tarih=planlanan_tarih,
            tamamlandi=tamamlandi,
            tamamlanma_tarihi=tamamlanma_tarihi,
            notlar=notlar
        )
        messages.success(request, 'Aşı takvimi kaydı eklendi!')
        return redirect('kullanici_paneli')
    return render(request, 'anahtarlik/asi_takvimi_ekle.html', {'evcil_hayvan': evcil_hayvan})

@login_required
def ilac_kaydi_ekle(request, evcil_hayvan_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=evcil_hayvan_id, sahip__kullanici=request.user)
    if request.method == 'POST':
        ilac_adi = request.POST.get('ilac_adi')
        baslangic_tarihi = request.POST.get('baslangic_tarihi')
        bitis_tarihi = request.POST.get('bitis_tarihi')
        dozaj = request.POST.get('dozaj')
        notlar = request.POST.get('notlar')
        IlacKaydi.objects.create(
            evcil_hayvan=evcil_hayvan,
            ilac_adi=ilac_adi,
            baslangic_tarihi=baslangic_tarihi,
            bitis_tarihi=bitis_tarihi,
            dozaj=dozaj,
            notlar=notlar
        )
        messages.success(request, 'İlaç kaydı eklendi!')
        return redirect('kullanici_paneli')
    return render(request, 'anahtarlik/ilac_kaydi_ekle.html', {'evcil_hayvan': evcil_hayvan})

@login_required
def ameliyat_kaydi_ekle(request, evcil_hayvan_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=evcil_hayvan_id, sahip__kullanici=request.user)
    if request.method == 'POST':
        ameliyat_turu = request.POST.get('ameliyat_turu')
        tarih = request.POST.get('tarih')
        veteriner = request.POST.get('veteriner')
        notlar = request.POST.get('notlar')
        AmeliyatKaydi.objects.create(
            evcil_hayvan=evcil_hayvan,
            ameliyat_turu=ameliyat_turu,
            tarih=tarih,
            veteriner=veteriner,
            notlar=notlar
        )
        messages.success(request, 'Ameliyat kaydı eklendi!')
        return redirect('kullanici_paneli')
    return render(request, 'anahtarlik/ameliyat_kaydi_ekle.html', {'evcil_hayvan': evcil_hayvan})

@login_required
def kilo_kaydi_ekle(request, evcil_hayvan_id):
    evcil_hayvan = get_object_or_404(EvcilHayvan, id=evcil_hayvan_id, sahip__kullanici=request.user)
    if request.method == 'POST':
        kilo = request.POST.get('kilo')
        tarih = request.POST.get('tarih')
        notlar = request.POST.get('notlar')
        KiloKaydi.objects.create(
            evcil_hayvan=evcil_hayvan,
            kilo=kilo,
            tarih=tarih,
            notlar=notlar
        )
        messages.success(request, 'Kilo kaydı eklendi!')
        return redirect('kullanici_paneli')
    return render(request, 'anahtarlik/kilo_kaydi_ekle.html', {'evcil_hayvan': evcil_hayvan})