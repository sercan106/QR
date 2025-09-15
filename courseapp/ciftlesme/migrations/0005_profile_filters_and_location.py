from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ciftlesme', '0004_seed_more_taxonomy'),
    ]

    operations = [
        migrations.AddField(
            model_name='matingprofile',
            name='allowed_breeds',
            field=models.ManyToManyField(blank=True, related_name='allowed_for_profiles', to='ciftlesme.breed'),
        ),
        migrations.AddField(
            model_name='matingprofile',
            name='require_vaccinated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='matingprofile',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='matingprofile',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

