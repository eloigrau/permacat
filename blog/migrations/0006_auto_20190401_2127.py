# Generated by Django 2.1.7 on 2019-04-01 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20190401_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projet',
            name='categorie',
            field=models.CharField(choices=[('Part', 'Participation à un évènement'), ('AGO', "Organisation d'une AGO"), ('Projlong', 'Projet a long terme'), ('Projcourt', 'Projet a court terme')], default='Part', max_length=30, verbose_name='categorie'),
        ),
    ]
