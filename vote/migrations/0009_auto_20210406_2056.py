# Generated by Django 2.2.13 on 2021-04-06 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0008_auto_20210312_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suffrage',
            name='date_dernierMessage',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date du dernier message'),
        ),
    ]
