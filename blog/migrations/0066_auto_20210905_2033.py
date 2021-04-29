# Generated by Django 2.2.24 on 2021-09-05 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0065_auto_20210905_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='categorie',
            field=models.CharField(choices=[('Annonce', 'Annonce'), ('Administratif', 'Administratif'), ('Agenda', 'Agenda'), ('Chantier', 'Atelier/Chantier participatif'), ('Documentation', 'Documentation'), ('covoit', 'Covoiturage'), ('Point', 'Idée / Point de vue'), ('Recette', 'Recette'), ('BonPlan', 'Bon Plan / achat groupé'), ('Divers', 'Divers'), ('Altermarché', 'Altermarché'), ('Ecovillage', 'Ecovillage'), ('Jardin', 'Jardins partagés')], default='Annonce', max_length=30, verbose_name='categorie'),
        ),
    ]
