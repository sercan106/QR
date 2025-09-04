# accaunt/views.py (Düzeltilmiş: date JSON serialize sorunu çözüldü)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from anahtarlik.models import Sahip, EvcilHayvan, Etiket
from accaunt.forms import EtiketForm, EvcilHayvanForm, KullaniciForm
from datetime import date  # date.fromisoformat için

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
                    # Kilitleme yok! sadece id'yi session'da tut
                    request.session['etiket_id'] = etiket.id
                    return redirect('step_2_pet_info')

            except Etiket.DoesNotExist:
                messages.error(request, "Bu seri numarası sistemde bulunamadı.")
    else:
        form = EtiketForm()
        
    return render(request, 'accaunt/register.html', {'form': form, 'step': 1})

def step_2_pet_info(request):
    if 'etiket_id' not in request.session:
        return redirect('step_1_check_tag')
    if request.method == 'POST':
        form = EvcilHayvanForm(request.POST)
        if form.is_valid():
            # Date'i JSON serializable hale getir (str'ye çevir)
            evcil_data = form.cleaned_data.copy()
            if 'dogum_tarihi' in evcil_data and evcil_data['dogum_tarihi']:
                evcil_data['dogum_tarihi'] = evcil_data['dogum_tarihi'].isoformat()
            request.session['evcil_data'] = evcil_data
            return redirect('step_3_owner_info')
    else:
        form = EvcilHayvanForm()
    return render(request, 'accaunt/register.html', {'form': form, 'step': 2})

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
                        adres=form.cleaned_data['adres']
                    )
                    # evcil_data'yı geri yükle, date'i date objesine çevir
                    evcil_data = request.session['evcil_data']
                    if 'dogum_tarihi' in evcil_data and evcil_data['dogum_tarihi']:
                        evcil_data['dogum_tarihi'] = date.fromisoformat(evcil_data['dogum_tarihi'])
                    evcil = EvcilHayvan.objects.create(sahip=sahip, **evcil_data)
                    etiket = Etiket.objects.get(id=request.session['etiket_id'])
                    etiket.evcil_hayvan = evcil
                    etiket.kilitli = False
                    etiket.aktif = True
                    etiket.save()
                    request.session.flush()
                    return redirect('step_4_complete')
    else:
        form = KullaniciForm()
    return render(request, 'accaunt/register.html', {'form': form, 'step': 3})

def step_4_complete(request):
    return render(request, 'accaunt/register_success.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('kullanici_paneli')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
            return render(request, 'accaunt/login.html')
    return render(request, 'accaunt/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('ev')