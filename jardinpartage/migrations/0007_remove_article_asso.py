# Generated by Django 2.2.13 on 2020-09-17 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jardinpartage', '0006_article_jardin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='asso',
        ),
    ]
