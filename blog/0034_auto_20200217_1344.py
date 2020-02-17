# Generated by Django 2.2.8 on 2020-02-17 12:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0033_auto_20200217_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evenement',
            name='end_time',
            field=models.DateTimeField(blank=True, help_text='jj/mm/année', null=True, verbose_name='Date de fin (optionnel pour un evenement sur plusieurs jours)'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='jj/mm/année', verbose_name='Date'),
        ),
    ]
