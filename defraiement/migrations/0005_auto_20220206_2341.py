# Generated by Django 2.2.24 on 2022-02-06 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defraiement', '0004_participantreunion_distance'),
    ]

    operations = [
        migrations.AddField(
            model_name='participantreunion',
            name='contexte_distance',
            field=models.TextField(blank=True, null=True, verbose_name='Description du contexte'),
        ),
        migrations.AlterField(
            model_name='participantreunion',
            name='distance',
            field=models.TextField(blank=True, null=True, verbose_name='Distance calculée'),
        ),
    ]