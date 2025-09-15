import csv
from django.core.management.base import BaseCommand, CommandError
from anahtarlik.dictionaries import Il, Ilce


class Command(BaseCommand):
    help = "Load provinces and districts from a CSV file with columns: il,ilce"

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to CSV file (utf-8)')

    def handle(self, *args, **options):
        path = options['csv_path']
        created_il = 0
        created_ilce = 0
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if 'il' not in reader.fieldnames or 'ilce' not in reader.fieldnames:
                    raise CommandError('CSV must have headers: il,ilce')
                for row in reader:
                    il_ad = (row['il'] or '').strip()
                    ilce_ad = (row['ilce'] or '').strip()
                    if not il_ad or not ilce_ad:
                        continue
                    il, created = Il.objects.get_or_create(ad=il_ad)
                    if created:
                        created_il += 1
                    _, created = Ilce.objects.get_or_create(il=il, ad=ilce_ad)
                    if created:
                        created_ilce += 1
        except FileNotFoundError:
            raise CommandError(f'File not found: {path}')

        self.stdout.write(self.style.SUCCESS(f'Loaded. New il: {created_il}, new ilce: {created_ilce}'))

