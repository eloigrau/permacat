# Generated by Django 2.1.3 on 2019-04-04 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_auto_20190403_2121'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commentaire',
            name='titre',
        ),
        migrations.RemoveField(
            model_name='commentaireprojet',
            name='titre',
        ),
        migrations.AddField(
            model_name='projet',
            name='coresponsable',
            field=models.CharField(blank=True, default='', max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='projet',
            name='date_modification',
            field=models.DateTimeField(auto_now=True, verbose_name='Date de dernière modification'),
        ),
        migrations.AddField(
            model_name='projet',
            name='lien_document',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='projet',
            name='lien_vote',
            field=models.URLField(blank=True, null=True),
        ),
    ]