# Generated by Django 2.2.24 on 2021-08-06 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0003_auto_20210806_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reponsequestion_b',
            name='choix',
            field=models.IntegerField(choices=[('', '-----------'), (0, 'Oui'), (1, 'Non'), (2, 'Ne se prononce pas')], default='', max_length=30, verbose_name='Choix du vote :'),
        ),
    ]
