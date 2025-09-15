# anahtarlik/admin.py

from django.contrib import admin, messages
from django import forms
from django.template.response import TemplateResponse
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils import timezone

from .models import (
    Sahip, EvcilHayvan, Etiket, Alerji, SaglikKaydi, AsiTakvimi,
    IlacKaydi, AmeliyatKaydi, BeslenmeKaydi, KiloKaydi
)
from .dictionaries import Tur, Cins, Il, Ilce

from veteriner.models import Veteriner
from petshop.models import Petshop

import qrcode
from io import BytesIO
import base64


@admin.register(Etiket)
class EtiketAdmin(admin.ModelAdmin):
    list_display = (
        'seri_numarasi', 'evcil_hayvan', 'aktif',
        'kanal', 'satici_veteriner', 'satici_petshop', 'tahsis_tarihi',
        'qr_kod_url_link', 'olusturulma_tarihi'
    )
    readonly_fields = ('etiket_id', 'qr_gorsel_onizleme', 'qr_kod_url', 'tahsis_tarihi')
    search_fields = ('seri_numarasi',)
    list_filter = ('aktif', 'kilitli', 'kanal', 'satici_veteriner', 'satici_petshop')
    actions = ['tahsis_aksiyonu']

    fieldsets = (
        ('Temel', {'fields': ('seri_numarasi', 'evcil_hayvan', 'aktif', 'kilitli')}),
        ('QR', {'fields': ('etiket_id', 'qr_kod_url', 'qr_gorsel_onizleme')}),
        ('Tahsis', {'fields': ('kanal', 'satici_veteriner', 'satici_petshop', 'tahsis_tarihi')}),
    )

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        # Tahsis yapıldıysa kanal ve partnerler kilitlensin (taşıma yasak)
        if obj and obj.tahsis_tarihi:
            ro += ['kanal', 'satici_veteriner', 'satici_petshop']
        return ro

    def save_model(self, request, obj, form, change):
        """Admin ekranında ilk kez tahsis girilirse sayaçları artır."""
        if not change:
            super().save_model(request, obj, form, change)
            return

        prev = Etiket.objects.get(pk=obj.pk)
        super().save_model(request, obj, form, change)

        # İlk kez tahsis girildiyse (önceden yoktu, şimdi var)
        if prev.tahsis_tarihi is None and obj.kanal:
            obj.tahsis_tarihi = timezone.now()
            obj.save(update_fields=['tahsis_tarihi'])
            obj._increase_allocation_counter()

    # ---- QR yardımcıları ----
    def qr_kod_url_link(self, obj):
        if obj.qr_kod_url:
            return format_html('<a href="{}" target="_blank">QR Link</a>', obj.qr_kod_url)
        return "Yok"
    qr_kod_url_link.short_description = "QR Kod URL"

    def qr_gorsel_onizleme(self, obj):
        if not obj.qr_kod_url:
            return "Henüz QR URL oluşturulmamış."
        qr = qrcode.make(obj.qr_kod_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        base64_image = base64.b64encode(buffer.getvalue()).decode()
        img_html = f'<img src="data:image/png;base64,{base64_image}" width="200" height="200" /><br>'
        download_link = (
            f'<a download="qr_{obj.seri_numarasi}.png" '
            f'href="data:image/png;base64,{base64_image}" '
            f'class="button btn btn-sm btn-success mt-2">İndir</a>'
        )
        return format_html(img_html + download_link)
    qr_gorsel_onizleme.short_description = "QR Önizleme & İndir"

    # ---- Toplu tahsis ----
    def get_urls(self):
        urls = super().get_urls()
        my = [path('tahsis/', self.admin_site.admin_view(self.tahsis_view), name='etiket_tahsis')]
        return my + urls

    def tahsis_aksiyonu(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if not selected:
            self.message_user(request, "Etiket seçmediniz.", level=messages.WARNING)
            return
        return redirect(f"{request.path}tahsis/?ids={','.join(selected)}")
    tahsis_aksiyonu.short_description = "Seçili etiketleri tahsis et"

    def tahsis_view(self, request):
        class TahsisForm(forms.Form):
            kanal = forms.ChoiceField(choices=Etiket.KANAL_SECENEKLERI, label="Kanal")
            veteriner = forms.ModelChoiceField(
                queryset=Veteriner.objects.filter(aktif=True),
                required=False,
                label="Veteriner"
            )
            petshop = forms.ModelChoiceField(
                queryset=Petshop.objects.filter(aktif=True),
                required=False,
                label="Petshop"
            )

            def clean(self):
                c = super().clean()
                k = c.get('kanal')
                v = c.get('veteriner')
                p = c.get('petshop')
                if k == Etiket.KANAL_VET and not v:
                    self.add_error('veteriner', "Veteriner seçin.")
                if k == Etiket.KANAL_SHOP and not p:
                    self.add_error('petshop', "Petshop seçin.")
                if k == Etiket.KANAL_ONLINE and (v or p):
                    raise forms.ValidationError("Online tahsiste partner seçmeyin.")
                return c

        ids = request.GET.get('ids') or request.POST.get('ids')
        if not ids:
            self.message_user(request, "Seçim yok.", level=messages.ERROR)
            return redirect('..')

        id_list = [int(x) for x in ids.split(',') if x]
        qs = Etiket.objects.filter(pk__in=id_list)

        if request.method == 'POST':
            form = TahsisForm(request.POST)
            if form.is_valid():
                k = form.cleaned_data['kanal']
                v = form.cleaned_data.get('veteriner')
                p = form.cleaned_data.get('petshop')

                done = 0
                skipped = 0
                for e in qs:
                    try:
                        e.tahsis_et(k, veteriner=v, petshop=p)
                        done += 1
                    except forms.ValidationError:
                        skipped += 1  # Zaten tahsisli olanlar atlanır

                self.message_user(
                    request,
                    f"{done} etiket tahsis edildi. {skipped} tahsisli olduğu için atlandı.",
                    level=messages.SUCCESS
                )
                return redirect('../')
        else:
            form = TahsisForm()

        ctx = dict(
            self.admin_site.each_context(request),
            title="Etiket Tahsis",
            form=form,
            ids=ids,
            queryset_display=qs[:50],
            total_count=qs.count(),
        )
        return TemplateResponse(request, 'admin/etiket_tahsis.html', ctx)


# ---------- Inline Modeller ----------
class AlerjiInline(admin.TabularInline):
    model = Alerji
    extra = 1
    fields = ('alerji_turu', 'aciklama', 'kaydedilme_tarihi')
    readonly_fields = ('kaydedilme_tarihi',)


class SaglikKaydiInline(admin.TabularInline):
    model = SaglikKaydi
    extra = 1
    fields = ('asi_turu', 'asi_tarihi', 'notlar')


class AsiTakvimiInline(admin.TabularInline):
    model = AsiTakvimi
    extra = 1
    fields = ('asi_turu', 'planlanan_tarih', 'tamamlandi', 'tamamlanma_tarihi', 'notlar')


class IlacKaydiInline(admin.TabularInline):
    model = IlacKaydi
    extra = 1
    fields = ('ilac_adi', 'baslangic_tarihi', 'bitis_tarihi', 'dozaj', 'notlar')


class AmeliyatKaydiInline(admin.TabularInline):
    model = AmeliyatKaydi
    extra = 1
    fields = ('ameliyat_turu', 'tarih', 'veteriner', 'notlar')


class BeslenmeKaydiInline(admin.TabularInline):
    model = BeslenmeKaydi
    extra = 1
    fields = ('besin_turu', 'tarih', 'miktar', 'notlar')


class KiloKaydiInline(admin.TabularInline):
    model = KiloKaydi
    extra = 1
    fields = ('kilo', 'tarih', 'notlar')


# ---------- Sözlükler: Tür, Cins, İl, İlçe ----------
@admin.register(Tur)
class TurAdmin(admin.ModelAdmin):
    search_fields = ("ad",)
    list_display = ("ad",)


@admin.register(Cins)
class CinsAdmin(admin.ModelAdmin):
    list_display = ("ad", "tur")
    list_filter = ("tur",)
    search_fields = ("ad", "tur__ad")


@admin.register(Il)
class IlAdmin(admin.ModelAdmin):
    search_fields = ("ad",)
    list_display = ("ad",)


@admin.register(Ilce)
class IlceAdmin(admin.ModelAdmin):
    list_display = ("ad", "il")
    list_filter = ("il",)
    search_fields = ("ad", "il__ad")


# ---------- Sahip ----------
@admin.register(Sahip)
class SahipAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'ad', 'soyad', 'telefon', 'adres')
    search_fields = ('kullanici__username', 'ad', 'soyad', 'telefon')
    list_filter = ('kullanici__is_active',)
    readonly_fields = ('kullanici',)


# ---------- Evcil Hayvan ----------
@admin.register(EvcilHayvan)
class EvcilHayvanAdmin(admin.ModelAdmin):
    list_display = ('ad', 'tur', 'cins', 'sahip', 'kayip_durumu_colored', 'resim_preview')
    search_fields = ('ad', 'cins', 'sahip__kullanici__username')
    list_filter = ('tur', 'kayip_durumu', 'cinsiyet')
    inlines = [
        AlerjiInline, SaglikKaydiInline, AsiTakvimiInline,
        IlacKaydiInline, AmeliyatKaydiInline, BeslenmeKaydiInline, KiloKaydiInline
    ]
    fieldsets = (
        ('Genel Bilgiler', {
            'fields': ('ad', 'tur', 'cins', 'cinsiyet', 'dogum_tarihi', 'sahip', 'resim', 'resim_preview')
        }),
        ('Ek Bilgiler', {
            'fields': ('saglik_notu', 'beslenme_notu', 'genel_not', 'davranis_notu')
        }),
        ('Kayıp Durumu', {
            'fields': ('kayip_durumu', 'kayip_bildirim_tarihi', 'odul_miktari')
        }),
    )
    readonly_fields = ('kayip_bildirim_tarihi', 'resim_preview')

    def kayip_durumu_colored(self, obj):
        color = 'red' if obj.kayip_durumu else 'green'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            'Kayıp' if obj.kayip_durumu else 'Güvende'
        )
    kayip_durumu_colored.short_description = 'Kayıp Durumu'

    def resim_preview(self, obj):
        if obj.resim:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 50%;" />',
                obj.resim.url
            )
        return 'Resim Yok'
    resim_preview.short_description = 'Resim Önizleme'


# ---------- Diğer Basit Modeller ----------
@admin.register(Alerji)
class AlerjiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'alerji_turu', 'kaydedilme_tarihi')
    search_fields = ('evcil_hayvan__ad', 'alerji_turu')
    list_filter = ('kaydedilme_tarihi',)


@admin.register(SaglikKaydi)
class SaglikKaydiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'asi_turu', 'asi_tarihi')
    search_fields = ('evcil_hayvan__ad', 'asi_turu')
    list_filter = ('asi_tarihi',)


@admin.register(AsiTakvimi)
class AsiTakvimiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'asi_turu', 'planlanan_tarih', 'tamamlandi')
    search_fields = ('evcil_hayvan__ad', 'asi_turu')
    list_filter = ('tamamlandi', 'planlanan_tarih')


@admin.register(IlacKaydi)
class IlacKaydiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'ilac_adi', 'baslangic_tarihi', 'bitis_tarihi')
    search_fields = ('evcil_hayvan__ad', 'ilac_adi')
    list_filter = ('baslangic_tarihi',)


@admin.register(AmeliyatKaydi)
class AmeliyatKaydiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'ameliyat_turu', 'tarih')
    search_fields = ('evcil_hayvan__ad', 'ameliyat_turu')
    list_filter = ('tarih',)


@admin.register(BeslenmeKaydi)
class BeslenmeKaydiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'besin_turu', 'tarih', 'miktar')
    search_fields = ('evcil_hayvan__ad', 'besin_turu')
    list_filter = ('tarih',)


@admin.register(KiloKaydi)
class KiloKaydiAdmin(admin.ModelAdmin):
    list_display = ('evcil_hayvan', 'kilo', 'tarih')
    search_fields = ('evcil_hayvan__ad',)
    list_filter = ('tarih',)






























# --- Kullanıcı Admini: tür sütunu + filtre ---
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class KullaniciTuruFilter(SimpleListFilter):
    title = "kullanıcı türü"
    parameter_name = "kullanici_turu"

    def lookups(self, request, model_admin):
        return (
            ("sahip", "QR Sahibi"),
            ("veteriner", "Veteriner"),
            ("petshop", "Petshop"),
            ("yok", "Profil yok"),
        )

    def queryset(self, request, queryset):
        v = self.value()
        if v == "sahip":
            return queryset.filter(sahip__isnull=False)  # OneToOneField (reverse adı: sahip)
        if v == "veteriner":
            return queryset.filter(veteriner_profili__isnull=False)  # related_name
        if v == "petshop":
            return queryset.filter(petshop_profili__isnull=False)     # related_name
        if v == "yok":
            return queryset.filter(
                sahip__isnull=True,
                veteriner_profili__isnull=True,
                petshop_profili__isnull=True,
            )
        return queryset

def kullanici_turu(obj: User):
    if hasattr(obj, "veteriner_profili"):
        return "Veteriner"
    if hasattr(obj, "petshop_profili"):
        return "Petshop"
    if hasattr(obj, "sahip"):
        return "QR Sahibi"
    return "—"
kullanici_turu.short_description = "Tür"
kullanici_turu.admin_order_field = None

# Varsayılan User adminini kaldırıp kendi sürümümüzü kaydediyoruz
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # mevcut sütunlara "kullanici_turu" ekle
    list_display = BaseUserAdmin.list_display + ("kullanici_turu",)
    # mevcut filtrelere özel filtreyi ekle
    list_filter = BaseUserAdmin.list_filter + (KullaniciTuruFilter,)

    def kullanici_turu(self, obj):
        return kullanici_turu(obj)
