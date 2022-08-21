# Generated by Django 2.2.28 on 2022-08-20 14:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0081_invitationdanssalon_date_creation'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscritsalon',
            name='date_creation',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date de création'),
            preserve_default=False,
        ),
    ]
