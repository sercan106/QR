# courseapp/context_processors.py (Global sepet context için)
from shop.models import Urun

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
