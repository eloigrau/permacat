# Generated by Django 2.2.24 on 2021-09-07 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0007_auto_20210819_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suffrage',
            name='end_time',
            field=models.DateField(help_text='jj/mm/année', null=True, verbose_name='Date de fin'),
        ),
        migrations.AlterField(
            model_name='suffrage',
            name='start_time',
            field=models.DateField(help_text='jj/mm/année', null=True, verbose_name='Date de début'),
        ),
    ]