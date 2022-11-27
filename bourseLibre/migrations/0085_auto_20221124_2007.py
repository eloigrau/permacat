# Generated by Django 2.2.28 on 2022-11-24 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0084_auto_20221030_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adhesion_asso',
            name='moyen',
            field=models.CharField(choices=[('0', 'Espèce'), ('1', 'HelloAsso'), ('2', 'Cheque'), ('3', 'Virement')], default='0', max_length=3, verbose_name='Moyen de maiement'),
        ),
        migrations.AlterField(
            model_name='adhesion_permacat',
            name='moyen',
            field=models.CharField(choices=[('0', 'Espèce'), ('1', 'HelloAsso'), ('2', 'Cheque'), ('3', 'Virement')], default='0', max_length=3, verbose_name='Moyen de maiement'),
        ),
    ]