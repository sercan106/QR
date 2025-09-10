# courseapp/context_processors.py (Global sepet context için)
from shop.models import Urun
from django.urls import reverse
from django.utils.functional import cached_property

def user_panel_target(request):
    """
    Kullanıcı paneli menüsü için hedef URL'yi belirler:
    - Veteriner: profil tamam ise veteriner paneli, değilse profil tamamlama
    - Petshop: profil tamamlama (panel yoksa), aksi halde panel
    - Son kullanıcı: evcil hayvan kullanıcı paneli
    """
    try:
        user = request.user
        if not user.is_authenticated:
            return { 'user_panel_url': reverse('user_login') }

        # Veteriner profili var mı?
        vet = getattr(user, 'veteriner_profili', None)
        if vet is not None:
            if not vet.il or not vet.adres_detay:
                return { 'user_panel_url': reverse('veteriner:veteriner_profil_tamamla') }
            return { 'user_panel_url': reverse('veteriner:veteriner_paneli') }

        # Petshop profili var mı?
        shop = getattr(user, 'petshop_profili', None)
        if shop is not None:
            # Panel URL'i tanımlı değilse profil tamamlama sayfasına yönlendir.
            try:
                return { 'user_panel_url': reverse('petshop:petshop_paneli') }
            except Exception:
                return { 'user_panel_url': reverse('petshop:petshop_profil_tamamla') }

        # Son kullanıcı (Sahip)
        return { 'user_panel_url': reverse('kullanici_paneli') }
    except Exception:
        # Her ihtimale karşı, kullanıcı paneline veya girişe düş
        try:
            return { 'user_panel_url': reverse('kullanici_paneli') }
        except Exception:
            return { 'user_panel_url': reverse('user_login') }

def sepet_ozeti(request):
    sepet = request.session.get('sepet', {})
    if isinstance(sepet, list):  # Eski liste ise dict'e çevir (hata önle)
        new_sepet = {}
        for pk in sepet:
            new_sepet[str(pk)] = new_sepet.get(str(pk), 0) + 1
        request.session['sepet'] = new_sepet
        sepet = new_sepet
    sepet_items = []
    toplam = 0
    adet = 0
    for pk, miktar in sepet.items():
        urun = Urun.objects.filter(pk=pk).first()
        if urun:
            subtotal = urun.fiyat * miktar
            sepet_items.append({'urun': urun, 'miktar': miktar, 'subtotal': subtotal})
            toplam += subtotal
            adet += miktar
    return {
        'sepet_items': sepet_items,
        'sepet_toplam': toplam,
        'sepet_adet': adet,
    }




# from wejegeh.models import Program_Anasayfa,Logos,Proje_anasayfa,Hakkimizda,Ev,Yayıncılık,Settings,Slide_index,Adres
# from wejegeh.models import ,Logo,Slide_anasayfa, Slide_b,

# def logo(request):
#     veri =  Logo.objects.all()
#     return {
#         'logo': veri #Genel temlateye logo ismi ile döndürdük
#     }

# def slide(request):
#     veri =  Slide_anasayfa.objects.all()
#     return {
#         'slide': veri #Genel temlateye logo ismi ile döndürdük
#     }

# def slide_b(request):
#     veri =  Slide_b.objects.all()
#     return {
#         'slide_b': veri #Genel temlateye logo ismi ile döndürdük
#     }

# def photoss(request):
#     veri =  Slide_index.objects.all()
#     return {
#         'photoss': veri #Genel temlateye logo ismi ile döndürdük
#     }


# def program_anasayfa(request):
#     veri =  Program_Anasayfa.objects.all()
#     return {
#         'program_anasayfa': veri #Genel temlateye logo ismi ile döndürdük
#     }

# def logolar_anasayfa(request):
#     veri =  Logos.objects.all()
#     return {
#         'logos': veri #Genel temlateye logo ismi ile döndürdük
#     }

# def projeanasayfa(request):
#     veri =  Proje_anasayfa.objects.all()
#     return {
#         'projeanasayfa': veri #Genel temlateye logo ismi ile döndürdük
#     }
# def hakkımızda(request):
#     veri =  Hakkimizda.objects.all()
#     return {
#         'hakkımızda': veri #Genel temlateye logo ismi ile döndürdük
#     }

# def ev(request):
#     veri =  Ev.objects.all()
#     return {
#         'ev': veri #Genel temlateye logo ismi ile döndürdük
#     }

# def yayıncılık(request):
#     veri =  Yayıncılık.objects.all()
#     return {
#         'yayıncılık': veri #Genel temlateye logo ismi ile döndürdük
#     }

# def ayar(request):
#     veri =  Settings.objects.all()
#     return {
#         'ayar': veri #Genel temlateye logo ismi ile döndürdük
#     }

# def adres(request):
#     veri =  Adres.objects.all()
#     return {
#         'adres': veri #Genel temlateye logo ismi ile döndürdük
#     }
