from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # 0019 and others were removed; point to the last existing migration
        ('anahtarlik', '0011_matingmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='sahip',
            name='il',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='sahip',
            name='ilce',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='sahip',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sahip',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
