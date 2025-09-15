# accaunt/views.py
# (role-aware login + mevcut 4 adımlı kayıt akışı)

from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone

from anahtarlik.models import Sahip, EvcilHayvan, Etiket
from accaunt.forms import EtiketForm
from accaunt.register_forms import EvcilHayvanKayitForm, KullaniciAdresForm
# Veteriner ve petshop modellerini de import edelim ki kontrol edebilelim
from veteriner.models import Veteriner
from petshop.models import Petshop


# --- 1. Adım: Etiket kontrolü ---
def step_1_check_tag(request):
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
                    return redirect('step_2_pet_info')
            except Etiket.DoesNotExist:
                messages.error(request, "Bu seri numarası sistemde bulunamadı.")
    else:
        form = EtiketForm()
    return render(request, 'accaunt/register.html', {'form': form, 'step': 1})


# --- 2. Adım: Pet bilgileri ---
def step_2_pet_info(request):
    if 'etiket_id' not in request.session:
        return redirect('step_1_check_tag')

    if request.method == 'POST':
        form = EvcilHayvanKayitForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            tur_obj = cd['tur']
            # cins seçimi: id ya da "__OTHER__"
            from anahtarlik.dictionaries import Cins
            cins_obj = None
            if cd.get('cins') == '__OTHER__':
                name = cd.get('cins_diger')
                if name:
                    cins_obj, _ = Cins.objects.get_or_create(tur=tur_obj, ad=name.strip())
            else:
                try:
                    cins_obj = Cins.objects.get(id=int(cd.get('cins'))) if cd.get('cins') else None
                except (Cins.DoesNotExist, ValueError, TypeError):
                    cins_obj = None
            tur_adi = tur_obj.ad
            cins_adi = cins_obj.ad if cins_obj else ''
            evcil_data = {
                'ad': cd.get('ad'),
                'tur': tur_adi or 'diger',
                'cins': cins_adi or '',
                'cinsiyet': cd.get('cinsiyet'),
                'dogum_tarihi': cd.get('dogum_tarihi').isoformat() if cd.get('dogum_tarihi') else None,
            }
            evcil_data['tur_ref_id'] = tur_obj.id
            evcil_data['cins_ref_id'] = cins_obj.id if cins_obj else None
            request.session['evcil_data'] = evcil_data
            return redirect('step_3_owner_info')
    else:
        form = EvcilHayvanKayitForm()
    return render(request, 'accaunt/register.html', {'form': form, 'step': 2})


# --- 3. Adım: Kullanıcı/Sahip bilgileri ---
def step_3_owner_info(request):
    if 'etiket_id' not in request.session or 'evcil_data' not in request.session:
        return redirect('step_1_check_tag')

    if request.method == 'POST':
        form = KullaniciAdresForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            telefon = form.cleaned_data['telefon']

            if User.objects.filter(username=username).exists():
                messages.error(request, "Kullanıcı adı zaten kullanılıyor.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Bu e-posta zaten kayıtlı.")
            elif Sahip.objects.filter(telefon=telefon).exists():
                messages.error(request, "Telefon numarası zaten kayıtlı.")
            else:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=form.cleaned_data['sifre']
                    )
                    sahip = Sahip.objects.create(
                        kullanici=user,
                        telefon=telefon,
                        ad=form.cleaned_data['ad'],
                        soyad=form.cleaned_data['soyad'],
                        yedek_telefon=form.cleaned_data['yedek_telefon'],
                        adres=form.cleaned_data['adres'],
                        il=form.cleaned_data['il'].ad,
                        ilce=form.cleaned_data['ilce'].ad,
                    )
                    # İlişkili il/ilçe referanslarını da kaydet
                    sahip.il_ref = form.cleaned_data['il']
                    sahip.ilce_ref = form.cleaned_data['ilce']
                    sahip.save(update_fields=['il_ref', 'ilce_ref'])
                    evcil_data = request.session['evcil_data']
                    if evcil_data.get('dogum_tarihi'):
                        evcil_data['dogum_tarihi'] = date.fromisoformat(evcil_data['dogum_tarihi'])

                    tur_ref_id = evcil_data.pop('tur_ref_id', None)
                    cins_ref_id = evcil_data.pop('cins_ref_id', None)
                    evcil = EvcilHayvan.objects.create(sahip=sahip, **evcil_data)
                    if tur_ref_id:
                        evcil.tur_ref_id = tur_ref_id
                    if cins_ref_id:
                        evcil.cins_ref_id = cins_ref_id
                    if tur_ref_id or cins_ref_id:
                        evcil.save(update_fields=[f for f,v in [('tur_ref',tur_ref_id),('cins_ref',cins_ref_id)] if v])

                    etiket = Etiket.objects.get(id=request.session['etiket_id'])
                    etiket.evcil_hayvan = evcil
                    etiket.kilitli = False
                    etiket.aktif = True
                    etiket.aktiflestiren = user
                    etiket.aktiflestirme_tarihi = timezone.now()
                    etiket.save()

                    request.session.flush()
                    return redirect('step_4_complete')
    else:
        form = KullaniciAdresForm()
    return render(request, 'accaunt/register.html', {'form': form, 'step': 3})


# --- AJAX: Seçilen tür için cinsleri getir ---
from django.http import JsonResponse
from anahtarlik.dictionaries import Cins, Ilce


def breeds_for_species(request):
    tur_id = request.GET.get('tur_id')
    try:
        tur_id = int(tur_id)
    except (TypeError, ValueError):
        return JsonResponse({'items': []})
    items = list(Cins.objects.filter(tur_id=tur_id).order_by('ad').values('id', 'ad'))
    return JsonResponse({'items': items})


def districts_for_province(request):
    il_id = request.GET.get('il_id')
    try:
        il_id = int(il_id)
    except (TypeError, ValueError):
        return JsonResponse({'items': []})
    items = list(Ilce.objects.filter(il_id=il_id).order_by('ad').values('id', 'ad'))
    return JsonResponse({'items': items})


# --- 4. Adım: Tamam ---
def step_4_complete(request):
    return render(request, 'accaunt/register_success.html')


# --- Giriş (ROL'E GÖRE YÖNLENDİRME) ---
def user_login(request):
    """
    Girişten sonra kullanıcı rolüne göre yönlendirir.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 1) Veteriner mi?
            if hasattr(user, "veteriner_profili"):
                v = user.veteriner_profili
                if not v.il or not v.adres_detay:
                    return redirect('veteriner:veteriner_profil_tamamla') # Düzeltme burada
                return redirect('veteriner:veteriner_paneli')

            # 2) Petshop mu?
            if hasattr(user, "petshop_profili"):
                s = user.petshop_profili
                if not s.il or not s.adres_detay:
                    return redirect('petshop:petshop_profil_tamamla') # Düzeltme burada
                return redirect('petshop:petshop_paneli')

            # 3) Son kullanıcı (Sahip)
            Sahip.objects.get_or_create(kullanici=user)
            return redirect('kullanici_paneli') # Bu URL'nin ad alanını da kontrol etmelisin

        messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
        return render(request, 'accaunt/login.html')

    return render(request, 'accaunt/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('ev')
