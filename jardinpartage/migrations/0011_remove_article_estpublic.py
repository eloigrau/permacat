# Generated by Django 2.2.13 on 2020-10-05 22:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jardinpartage', '0010_auto_20200918_0001'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='estPublic',
        ),
    ]
