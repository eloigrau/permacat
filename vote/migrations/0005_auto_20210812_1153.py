# Generated by Django 2.2.24 on 2021-08-12 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0004_auto_20210806_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reponsequestion_b',
            name='choix',
            field=models.IntegerField(choices=[('', '-----------'), (0, 'Oui'), (1, 'Non'), (2, 'Ne se prononce pas')], default='', verbose_name='Choix du vote :'),
        ),
    ]
