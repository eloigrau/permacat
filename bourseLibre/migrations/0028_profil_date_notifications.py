# Generated by Django 2.2.8 on 2019-12-12 19:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0027_inscriptionnewsletter'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='date_notifications',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de validationd es notifications'),
        ),
    ]
