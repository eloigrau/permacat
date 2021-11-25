# Generated by Django 2.2.24 on 2021-07-26 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0058_auto_20210619_2341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='categorie',
            field=models.CharField(choices=[('Annonce', 'Annonces'), ('Administratif', 'Administratif'), ('Agenda', 'Agenda'), ('Chantier', 'Ateliers/Chantiers participatifs'), ('Documentation', 'Documentation'), ('Point', 'Point de vue'), ('Recette', 'Recettes'), ('BonPlan', 'Bons Plans / achats groupés'), ('Divers', 'Divers'), ('Altermarché', 'Altermarché'), ('Ecovillage', 'Ecovillage'), ('Jardin', 'Jardins partagés')], default='Annonce', max_length=30, verbose_name='categorie'),
        ),
    ]