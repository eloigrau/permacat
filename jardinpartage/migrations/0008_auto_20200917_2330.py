# Generated by Django 2.2.13 on 2020-09-17 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jardinpartage', '0007_remove_article_asso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='jardin',
            field=models.CharField(choices=[('0', 'Tous jardins'), ('1', 'Jardi Per Tots'), ('1', 'JardiPal')], default='0', max_length=30, verbose_name='Jardin'),
        ),
    ]
