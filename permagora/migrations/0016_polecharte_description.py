# Generated by Django 2.2.27 on 2022-08-01 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permagora', '0015_auto_20220801_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='polecharte',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]