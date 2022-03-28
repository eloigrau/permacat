# Generated by Django 2.2.27 on 2022-03-28 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0082_article_estepingle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='categorie',
            field=models.CharField(choices=[('Annonce', 'Annonce'), ('Administratif', 'Organisation'), ('Agenda', 'Agenda'), ('Chantier', 'Atelier/Chantier participatif'), ('Documentation', 'Documentation'), ('covoit', 'Covoiturage'), ('Point', 'Idée / Point de vue'), ('Recette', 'Recette'), ('BonPlan', 'Bon Plan / achat groupé'), ('Divers', 'Divers'), ('orga1', 'Cercle Organisation'), ('orga2', 'Cercle Informatique'), ('orga3', 'Cercle Communication'), ('orga4', 'Cercle Animation'), ('orga5', 'Cercle Médiation'), ('theme1', 'Cercle Education'), ('theme2', 'Cercle Ecolieux'), ('theme3', 'Cercle Santé'), ('theme4', 'Cercle Echanges'), ('theme5', 'Cercle Agriculture'), ('theme6', 'Cercle Célébration'), ('groupe1', 'Groupe de Perpignan'), ('groupe2', 'Groupe des Albères'), ('groupe3', 'Groupe des Aspres'), ('groupe4', 'Groupe du Vallespir'), ('groupe5', 'Groupe du Ribéral'), ('groupe7', 'Groupe du Conflent'), ('groupe6', 'Groupe de la côte'), ('Info', 'Annonce / Information'), ('Agenda', 'Agenda'), ('coordination', 'Coordination'), ('reunion', 'Réunions'), ('manifestations', 'Manifestations'), ('Altermarché', 'Altermarché'), ('Ecovillage', 'Ecovillage'), ('Jardin', 'Jardins partagés'), ('ChantPossible', 'Ecolieu Chant des possibles'), ('BD_Fred', 'Les BD de Frédéric')], default='', max_length=30, verbose_name='Dossier'),
        ),
    ]
