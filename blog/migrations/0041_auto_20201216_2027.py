# Generated by Django 2.2.13 on 2020-12-16 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0040_auto_20201215_0014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='categorie',
            field=models.CharField(choices=[('Annonce', 'Annonce'), ('Administratif', 'Administratif'), ('Agenda', 'Agenda'), ('Chantier', 'Chantier participatif'), ('Documentation', 'Documentation'), ('Point', 'Point de vue'), ('Recette', 'Recette'), ('Divers', 'Divers'), ('Altermarché', 'Altermarché'), ('Ecovillage', 'Ecovillage'), ('Jardin', 'Jardins partagés')], default='Annonce', max_length=30, verbose_name='categorie'),
        ),
    ]
