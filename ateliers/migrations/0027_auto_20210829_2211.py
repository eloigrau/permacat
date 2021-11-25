# Generated by Django 2.2.24 on 2021-08-29 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ateliers', '0026_auto_20210715_2351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atelier',
            name='statut',
            field=models.CharField(choices=[('0', 'proposition'), ('1', "accepté, en cours d'organisation"), ('2', "accepté, s'est déroule correctement"), ('3', 'a été annulé')], default='proposition', max_length=30, verbose_name="Statut de l'atelier"),
        ),
    ]