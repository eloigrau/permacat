# Generated by Django 2.2.20 on 2021-05-26 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jardinpartage', '0014_auto_20210222_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='estModifiable',
            field=models.BooleanField(default=False, verbose_name='Modifiable par les autres'),
        ),
    ]
