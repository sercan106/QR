# anahtarlik/urls.py

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ev, name='ev'),
    path('tag/', views.tag, name='tag'),
    path('etiket/<uuid:etiket_id>/', views.etiket_goruntule, name='etiket_goruntule'),

    # Kullanıcı Paneli
    path('panel/', views.kullanici_paneli, name='kullanici_paneli'),
    path('panel/add-pet/', views.add_pet, name='add_pet'),
    path('panel/pet/<int:pet_id>/', views.pet_detail, name='pet_detail'),
    path('panel/pet/<int:pet_id>/pdf/', views.hayvan_pdf_indir, name='hayvan_pdf_indir'),
    path('panel/profil-duzenle/', views.profil_duzenle, name='profil_duzenle'),


    # Evcil hayvan işlemleri
    path('panel/kayip-bildir/<int:evcil_hayvan_id>/', views.kayip_bildir, name='kayip_bildir'),
    path('panel/saglik-kaydi/<int:evcil_hayvan_id>/', views.saglik_kaydi_ekle, name='saglik_kaydi_ekle'),
    path('panel/beslenme-kaydi/<int:evcil_hayvan_id>/', views.beslenme_kaydi_ekle, name='beslenme_kaydi_ekle'),
    path('panel/edit-pet/<int:pet_id>/', views.edit_pet, name='edit_pet'),
    path('panel/delete-pet/<int:pet_id>/', views.delete_pet, name='delete_pet'),
    path('panel/alerji-ekle/<int:evcil_hayvan_id>/', views.alerji_ekle, name='alerji_ekle'),
    path('panel/asi-takvimi-ekle/<int:evcil_hayvan_id>/', views.asi_takvimi_ekle, name='asi_takvimi_ekle'),
    path('panel/ilac-kaydi-ekle/<int:evcil_hayvan_id>/', views.ilac_kaydi_ekle, name='ilac_kaydi_ekle'),
    path('panel/ameliyat-kaydi-ekle/<int:evcil_hayvan_id>/', views.ameliyat_kaydi_ekle, name='ameliyat_kaydi_ekle'),
    path('panel/kilo-kaydi-ekle/<int:evcil_hayvan_id>/', views.kilo_kaydi_ekle, name='kilo_kaydi_ekle'),

    # Django login/logout
    path('auth/', include('django.contrib.auth.urls')),
]
















    # path('deneme', views.deneme),
    # path('ev', views.ev), 
    # path('hakkımızda', views.hakkımızda),  
    # path('yayıncılık', views.yayıncılık),  
    # path('program', views.program), 
    # path('program/<slug:slug>/', views.program_detail, name='program_detail'),
    # path('program/<str:kategori>/<slug:slug>/', views.program_etkinlik, name='program_etkinlik'),
    # path('program/<slug:slug>/', views.program_detail, name='program_detail'),
    # path('logo', views.logo), 
    # path('projeler', views.projeler),
    # path('projeler/<slug:slug>/', views.proje, name='proje'),
    # path('projeler/<str:kategori>/<slug:slug>/', views.proje_etkinlik, name='proje_etkinlik'),

    # path('arşiv/<str:kategori>/<str:kategori2>/', views.arşiv_detay, name='arşiv_detay'),
    # path('arşiv', views.arşiv),



    # path('search_results/', views.search_results, name='search_results'),



    # path('hakkında', views.hakkında, name='hakkında'),
    # path('shop', views.shop, name='shop'),
    # path('contact', views.contact, name='contact'),
    # path('urun_ekle', views.urun_ekle, name='urun_ekle'),
    # path('urun_detay/<slug:slug>/<int:id>', views.urun_detay, name='urun_detay'),





# urlpatterns = [
#     path('', views.home),
#     path('borc', views.borc, name='borc'),
#     path('sonuc/<int:id>', views.sonuc, name='sonuc'),
#     path('gıda', views.gıda, name='gıda'),
#     path('aileharcama', views.aileharcama, name='aileharcama'),
#     path('kartlar', views.kartlar, name='kartlar'),
#     path('analiz', views.analiz, name='analiz'),
#     path('silgıdaharcama', views.silgıdaharcama, name='silgıdaharcama'),
    
#     path('silsercanharcama', views.silsercanharcama, name='silsercanharcama'),
#     path('silmehmetharcama', views.silmehmetharcama, name='silmehmetharcama'),
#     path('silerenharcama', views.silerenharcama, name='silerenharcama'),

#     path('sercanharcama', views.sercanharcama, name='sercanharcama'),
#     path('mehmetharcama', views.mehmetharcama, name='mehmetharcama'),
#     path('erenharcama', views.erenharcama, name='erenharcama'),



#     #______________SİL_______________________
#     path('kart_sil/<int:id>', views.kart_sil, name='kart_sil'),
#     path('sil/<int:id>', views.sil, name='sil'),
#     path('gıda_sil/<int:id>', views.gıda_sil, name='gıda_sil'),


#     #_____________________EKLE________________
#     path('ekle', views.ekle, name='ekle'),
#     path('kart_ekle', views.kart_ekle, name='kart_ekle'),
#     path('eklegıda', views.eklegıda, name='eklegıda'),
#     path('gıdaisimekle', views.gıdaisimekle, name='gıdaisimekle')

    




    # path('iletişim', views.kurslar),
    # path('search', views.search, name='search'),#arama sayfası burası
    # path('post', views.post, name='post'),#post
    # path('post2', views.post2, name='post2'),#post etme ve girilen verileri kontrol etme
    # path('ürün_detay', views.ürün_detay, name='ürün_detay'),
    # path('güncelle/<int:idurls>', views.güncelle, name='güncelle'),
    # path('sil/<int:idurls>', views.sil, name='sil'),
    # path('yükle', views.yükle, name='resim_yükle'),
    # path('index', views.index),
    # path('index/<int:kategori>', views.kategori),
    # path('veritabanı', views.veritabanı),
    
    # path('anasayfa', views.anasayfa),
    # path('<int:kategori>',views.dinamik),#burda ketegori değişkenimizi oluşturduk.Eğer str türünde veri
    # #alırsa views.dinamik çalışır
    # #not:yukarıdan aşağıya okuma yaptığı için üstte şartı karşılayan bir path varsa onu görür 
    # #aşağıdakileri görmez.
    # path('<str:kategori>',views.dinamikstr),
# ]
    

