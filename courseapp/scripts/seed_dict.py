import os
import sys
import django

# Ensure project root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courseapp.settings')
django.setup()

from anahtarlik.dictionaries import Tur, Cins, Il, Ilce


def run():
    Tur.objects.get_or_create(ad='Kedi')
    Tur.objects.get_or_create(ad='Köpek')
    Tur.objects.get_or_create(ad='Tavşan')

    kedi = Tur.objects.get(ad='Kedi')
    Cins.objects.get_or_create(tur=kedi, ad='British Shorthair')
    Cins.objects.get_or_create(tur=kedi, ad='Scottish Fold')

    kopek = Tur.objects.get(ad='Köpek')
    Cins.objects.get_or_create(tur=kopek, ad='Golden Retriever')
    Cins.objects.get_or_create(tur=kopek, ad='Labrador Retriever')

    istanbul, _ = Il.objects.get_or_create(ad='İstanbul')
    ankara, _ = Il.objects.get_or_create(ad='Ankara')
    izmir, _ = Il.objects.get_or_create(ad='İzmir')

    for il, ad in [
        (istanbul, 'Kadıköy'),
        (istanbul, 'Beşiktaş'),
        (istanbul, 'Üsküdar'),
        (ankara, 'Çankaya'),
        (ankara, 'Keçiören'),
        (izmir, 'Konak'),
    ]:
        Ilce.objects.get_or_create(il=il, ad=ad)

    print('Seeded sample dictionary data.')


if __name__ == '__main__':
    run()
