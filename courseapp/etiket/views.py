# etiket/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from anahtarlik.models import Etiket
from .forms import SeriNumaraForm
import qrcode
import io
import logging
import requests

logger = logging.getLogger(__name__)


# 1. QR TARANDIĞINDA AÇILAN SAYFA VE E-POSTA GÖNDERİMİ
def qr_landing_view(request, tag_id):
    etiket = get_object_or_404(Etiket, etiket_id=tag_id)
    hayvan = etiket.evcil_hayvan
    sahip = hayvan.sahip

    logger.info("📌 [qr_landing_view] view'e giriş yapıldı.")
    logger.info(f"🐾 Hayvan: {hayvan.ad}")
    logger.info(f"👤 Sahip: {sahip.ad} {sahip.soyad}")
    logger.info(f"📧 Sahip e-posta: {sahip.kullanici.email}")

    # IP adresi
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Bilinmiyor')).split(',')[0].strip()

    # Konum bilgisi (ipinfo.io)
    konum_bilgi = "Konum alınamadı"
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3)
        if response.status_code == 200:
            data = response.json()
            sehir = data.get('city', '-')
            bolge = data.get('region', '-')
            ulke = data.get('country', '-')
            konum_bilgi = f"{sehir}, {bolge}, {ulke}"
    except Exception as e:
        logger.warning(f"🌐 Konum alınamadı: {e}")

    # Tarayıcı bilgileri
    user_agent = request.META.get('HTTP_USER_AGENT', 'Bilinmiyor')
    tarayici_dili = request.META.get('HTTP_ACCEPT_LANGUAGE', 'Bilinmiyor')

    # Zaman bilgisi
    zaman = timezone.now().strftime("%d.%m.%Y %H:%M")

    # Sayfa URL'si
    qr_link = request.build_absolute_uri()

    # Bildirim tarihi ve ödül
    bildirim_tarihi = hayvan.kayip_bildirim_tarihi.strftime('%d.%m.%Y %H:%M') if hayvan.kayip_bildirim_tarihi else "Bildirilmemiş"
    odul = f"{hayvan.odul_miktari} ₺" if hayvan.odul_miktari else "Belirtilmedi"

    # Mail gönderimi
    subject = f"📍 {hayvan.ad} adlı evcil hayvanınız tarandı!"
    message = f"""
Merhaba {sahip.ad},

{hayvan.ad} adlı evcil hayvanınıza ait QR etiketi az önce bir kullanıcı tarafından tarandı.

📅 Tarama Tarihi: {zaman}
📍 IP Adresi: {ip}
🌍 Lokasyon (IP üzerinden): {konum_bilgi}
💻 Cihaz ve Tarayıcı: {user_agent}
🗣️ Tarayıcı Dili: {tarayici_dili}
🔗 Tarama Sayfası: {qr_link}

🐾 Hayvan Bilgisi:
- Adı: {hayvan.ad}
- Tür: {hayvan.get_tur_display()}
- Kayıp Bildirimi: {bildirim_tarihi}
- Ödül: {odul}

Lütfen bu bildirimi dikkate alın.  
Anahtarlık Ekibi olarak geçmiş olsun dileklerimizi sunarız.
""".strip()

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [sahip.kullanici.email],
            fail_silently=False,
        )
        logger.info(f"✅ E-Posta gönderildi: {sahip.kullanici.email}")
    except Exception as e:
        logger.error(f"❌ E-Posta gönderim hatası: {e}")

    return render(request, 'etiket/qr_landing.html', {
        'etiket': etiket,
        'hayvan': hayvan
    })


# 2. SERİ NUMARASIYLA YÖNLENDİRME
def qr_by_serial_view(request, serial_number):
    try:
        etiket = Etiket.objects.get(seri_numarasi=serial_number)
        return redirect('etiket:qr_landing', tag_id=etiket.etiket_id)
    except Etiket.DoesNotExist:
        messages.error(request, "❌ Bu seri numarasına ait etiket bulunamadı.")
        return redirect('etiket:lookup')


# 3. QR KODUNU OLUŞTUR VE İNDİR
def qr_download_view(request, tag_id):
    etiket = get_object_or_404(Etiket, etiket_id=tag_id)
    qr_url = request.build_absolute_uri(
        redirect('etiket:qr_landing', tag_id=etiket.etiket_id).url
    )

    qr = qrcode.make(qr_url)
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="etiket_{etiket.seri_numarasi}.png"'
    return response


# 4. KONUM BİLDİRİMİ (DUMMY SAYFA)
def qr_notify_location(request, tag_id):
    etiket = get_object_or_404(Etiket, etiket_id=tag_id)
    return render(request, 'etiket/notify_success.html', {
        'etiket': etiket,
        'hayvan': etiket.evcil_hayvan
    })


# 5. MANUEL SERİ NUMARA ARAMA FORMU
def serial_number_lookup_view(request):
    form = SeriNumaraForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            serial_number = form.cleaned_data['seri_numarasi']
            return redirect('etiket:qr_by_serial', serial_number=serial_number)

    return render(request, 'etiket/serial_lookup_form.html', {'form': form})
