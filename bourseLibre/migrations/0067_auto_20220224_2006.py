# Generated by Django 2.2.27 on 2022-02-24 19:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0066_auto_20220224_1941'),
    ]

    operations = [
        migrations.CreateModel(
            name='Produit_listeOffresEtDemandes',
            fields=[
                ('produit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bourseLibre.Produit')),
                ('couleur', models.CharField(choices=[('#ccddff', '#ccddff')], default='#ccddff', max_length=20)),
                ('souscategorie', models.CharField(choices=[('L', 'L'), ('i', 'i'), ('s', 's'), ('t', 't'), ('e', 'e'), (' ', ' '), ('v', 'v'), ('a', 'a'), ('r', 'r'), ('i', 'i'), ('é', 'é'), ('e', 'e')], default='L', max_length=20)),
                ('type_prix', models.CharField(choices=[('kg', 'kg'), ('100g', '100g'), ('10g', '10g'), ('g', 'g'), ('un', 'unité'), ('li', 'litre')], default='kg', max_length=20, verbose_name='par')),
            ],
            bases=('bourseLibre.produit',),
        ),
        migrations.AlterField(
            model_name='produit',
            name='categorie',
            field=models.CharField(choices=[('aliment', 'aliment'), ('vegetal', 'végétal'), ('service', 'service'), ('objet', 'objet'), ('liste', 'liste des offres et demandes')], default='aliment', max_length=20),
        ),
    ]