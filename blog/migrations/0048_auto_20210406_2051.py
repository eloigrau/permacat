# Generated by Django 2.2.13 on 2021-04-06 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0047_auto_20210315_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projet',
            name='date_dernierMessage',
            field=models.DateTimeField(verbose_name='Date de Modification'),
        ),
    ]