# Generated by Django 2.2.27 on 2022-04-12 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agoratransition', '0007_auto_20220412_0932'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='proposition',
            unique_together={('proposition', 'email')},
        ),
    ]
