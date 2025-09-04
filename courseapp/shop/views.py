from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.db.models import Q
from django.conf import settings

from .models import Urun, Siparis, SiparisKalemi, Kategori, UrunResim
from .forms import SiparisFormu

from stripe import PaymentIntent  # pip install stripe


class ShopHomeView(ListView):
    model = Urun
    template_name = 'shop/shop_home.html'
    context_object_name = 'urunler'

    def get_queryset(self):
        queryset = super().get_queryset()
        kategori_slug = self.request.GET.get('kategori')
        search_query = self.request.GET.get('q')

        if kategori_slug:
            queryset = queryset.filter(kategori__slug=kategori_slug)

        if search_query:
            queryset = queryset.filter(ad__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kategoriler'] = Kategori.objects.all()
        return context


def product_detail(request, pk):
    urun = get_object_or_404(Urun, pk=pk)
    resimler = urun.resimler.all()
    return render(request, 'shop/product_detail.html', {
        'urun': urun,
        'resimler': resimler,
    })


def add_to_cart(request, pk):
    urun = get_object_or_404(Urun, pk=pk)
    if urun.stok <= 0:
        messages.error(request, f"{urun.ad} stokta yok!")
        return redirect('shop_home')

    sepet = request.session.get('sepet', {})
    sepet[str(pk)] = sepet.get(str(pk), 0) + 1
    request.session['sepet'] = sepet
    messages.success(request, f"{urun.ad} sepete eklendi!")
    return redirect('shop_home')


def cart_view(request):
    sepet = request.session.get('sepet', {})
    urunler = []
    toplam = 0

    for pk, miktar in sepet.items():
        urun = get_object_or_404(Urun, pk=pk)

        if urun.stok < miktar:
            messages.warning(request, f"{urun.ad} stok yetersiz, miktar azaltıldı.")
            miktar = urun.stok
            sepet[pk] = miktar

        if miktar > 0:
            subtotal = urun.fiyat * miktar
            urunler.append({
                'urun': urun,
                'miktar': miktar,
                'subtotal': subtotal
            })
            toplam += subtotal

    request.session['sepet'] = sepet
    return render(request, 'shop/cart.html', {
        'urunler': urunler,
        'toplam': toplam
    })


def remove_from_cart(request, pk):
    sepet = request.session.get('sepet', {})
    if str(pk) in sepet:
        del sepet[str(pk)]
        request.session['sepet'] = sepet
        messages.success(request, "Ürün sepetten kaldırıldı.")
    return redirect('cart_view')


def update_cart_quantity(request, pk):
    sepet = request.session.get('sepet', {})
    if str(pk) in sepet:
        miktar = int(request.POST.get('miktar', 1))
        urun = get_object_or_404(Urun, pk=pk)

        if miktar > urun.stok:
            miktar = urun.stok
            messages.warning(request, f"Maksimum {urun.stok} adet eklenebilir.")

        if miktar <= 0:
            del sepet[str(pk)]
        else:
            sepet[str(pk)] = miktar

        request.session['sepet'] = sepet

    return redirect('cart_view')


@login_required
def checkout(request):
    sepet = request.session.get('sepet', {})
    if not sepet:
        return redirect('cart_view')

    urunler = []
    toplam = 0

    for pk, miktar in sepet.items():
        urun = get_object_or_404(Urun, pk=pk)
        subtotal = urun.fiyat * miktar
        urunler.append({
            'urun': urun,
            'miktar': miktar,
            'subtotal': subtotal
        })
        toplam += subtotal

    if request.method == 'POST':
        form = SiparisFormu(request.POST)
        if form.is_valid():
            siparis = Siparis.objects.create(
                kullanici=request.user,
                toplam_fiyat=toplam,
                adres=form.cleaned_data['adres']
            )

            for item in urunler:
                SiparisKalemi.objects.create(
                    siparis=siparis,
                    urun=item['urun'],
                    miktar=item['miktar'],
                    fiyat=item['urun'].fiyat
                )

                # TODO: Sipariş sonrası stok düşür
                item['urun'].stok -= item['miktar']
                item['urun'].save()

            # TODO: E-posta bildirimi gönderilebilir

            # Stripe Ödeme Başlat
            payment_intent = PaymentIntent.create(
                amount=int(toplam * 100),  # Cent cinsinden
                currency="try",
                payment_method_types=['card'],
                metadata={'siparis_id': siparis.id},
            )

            request.session['payment_intent_id'] = payment_intent.id
            return redirect('payment_confirm')
    else:
        form = SiparisFormu()

    return render(request, 'shop/checkout.html', {
        'form': form,
        'toplam': toplam,
        'urunler': urunler,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })


@login_required
def payment_confirm(request):
    payment_intent_id = request.session.get('payment_intent_id')
    if not payment_intent_id:
        return redirect('cart_view')

    # TODO: Stripe ödeme durumu kontrol edilebilir (gelişmiş entegrasyon için)
    request.session.pop('sepet', None)
    request.session.pop('payment_intent_id', None)

    messages.success(request, "Ödeme başarılı! Siparişiniz alındı.")
    return redirect('order_history')


@login_required
def order_history(request):
    siparisler = Siparis.objects.filter(kullanici=request.user).order_by('-olusturulma_tarihi')
    return render(request, 'shop/order_history.html', {
        'siparisler': siparisler
    })
