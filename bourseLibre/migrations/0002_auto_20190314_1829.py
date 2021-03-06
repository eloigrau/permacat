# Generated by Django 2.1.7 on 2019-03-14 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produit_aliment',
            name='etat',
        ),
        migrations.RemoveField(
            model_name='produit_objet',
            name='etat',
        ),
        migrations.RemoveField(
            model_name='produit_service',
            name='etat',
        ),
        migrations.RemoveField(
            model_name='produit_vegetal',
            name='etat',
        ),
        migrations.AddField(
            model_name='adresse',
            name='commune',
            field=models.CharField(blank=True, default='Perpignan', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='produit',
            name='date_debut',
            field=models.DateField(blank=True, null=True, verbose_name='Débute le : (mm/jj/an)'),
        ),
        migrations.AlterField(
            model_name='produit',
            name='date_expiration',
            field=models.DateField(blank=True, null=True, verbose_name='Expire le : (jj/mm/an)'),
        ),
        migrations.AlterField(
            model_name='produit_objet',
            name='souscategorie',
            field=models.CharField(choices=[('jardinage', 'jardinage'), ('outillage', 'outillage'), ('vehicule', 'vehicule'), ('multimedia', 'multimedia'), ('mobilier', 'mobilier'), ('construction', 'construction'), ('autre', 'autre')], default='j', max_length=20),
        ),
        migrations.AlterField(
            model_name='produit_service',
            name='souscategorie',
            field=models.CharField(choices=[('jardinage', 'jardinage'), ('cuisine', 'cuisine'), ('éducation', 'éducation'), ('soins', 'soins'), ('bien être', 'bien être'), ('informatique', 'informatique'), ('batiment', 'batiment'), ('mecanique', 'mecanique'), ('autre', 'autre')], default='j', max_length=20),
        ),
        migrations.AlterField(
            model_name='produit_vegetal',
            name='souscategorie',
            field=models.CharField(choices=[('graines', 'graines'), ('fleurs', 'fleurs'), ('plantes', 'plantes'), ('jeunes plans', 'jeunes plans'), ('purins', 'purins'), ('autre', 'autre')], default='g', max_length=20),
        ),
        migrations.AddField(
            model_name='produit',
            name='estPublique',
            field=models.BooleanField(default=False, verbose_name='Publique (cochez) ou Interne (décochez)'),
        ),
        migrations.AddField(
            model_name='profil',
            name='pseudo_june',
            field=models.CharField(default=None, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, null=True, unique=True, verbose_name='pseudo Monnaie Libre'),
        ),
    ]
