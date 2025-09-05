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
from accaunt.forms import EtiketForm, EvcilHayvanForm, KullaniciForm
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
        form = EvcilHayvanForm(request.POST)
        if form.is_valid():
            evcil_data = form.cleaned_data.copy()
            if evcil_data.get('dogum_tarihi'):
                evcil_data['dogum_tarihi'] = evcil_data['dogum_tarihi'].isoformat()
            request.session['evcil_data'] = evcil_data
            return redirect('step_3_owner_info')
    else:
        form = EvcilHayvanForm()
    return render(request, 'accaunt/register.html', {'form': form, 'step': 2})


# --- 3. Adım: Kullanıcı/Sahip bilgileri ---
def step_3_owner_info(request):
    if 'etiket_id' not in request.session or 'evcil_data' not in request.session:
        return redirect('step_1_check_tag')

    if request.method == 'POST':
        form = KullaniciForm(request.POST)
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
                        adres=form.cleaned_data['adres']
                    )
                    evcil_data = request.session['evcil_data']
                    if evcil_data.get('dogum_tarihi'):
                        evcil_data['dogum_tarihi'] = date.fromisoformat(evcil_data['dogum_tarihi'])

                    evcil = EvcilHayvan.objects.create(sahip=sahip, **evcil_data)

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
        form = KullaniciForm()
    return render(request, 'accaunt/register.html', {'form': form, 'step': 3})


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