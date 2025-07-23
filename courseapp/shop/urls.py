# shop/urls.py (Path'ler İngilizce)

from django.urls import path
from . import views

urlpatterns = [
    path('', views.ShopHomeView.as_view(), name='shop_home'),  # ListView'e güncellendi
    path('urun/<int:pk>/', views.product_detail, name='product_detail'),
    path('sepete-ekle/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('sepet/', views.cart_view, name='cart_view'),
    path('sepetten-cikar/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('sepet-guncelle/<int:pk>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('odeme/', views.checkout, name='checkout'),
    path('odeme-onay/', views.payment_confirm, name='payment_confirm'),
    path('siparis-gecmisi/', views.order_history, name='order_history'),
    
]