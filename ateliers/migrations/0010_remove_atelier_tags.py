# Generated by Django 2.2.8 on 2019-12-09 18:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ateliers', '0009_atelier_heure_atelier'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='atelier',
            name='tags',
        ),
    ]