# Generated by Django 2.2.27 on 2022-03-23 23:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InscriptionExposant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.TextField(blank=True, verbose_name='Nom prénom / Raison sociale')),
                ('nom_structure', models.TextField(blank=True, verbose_name='Nom de la structure, association, autre')),
                ('telephone', models.CharField(blank=True, max_length=10, validators=[django.core.validators.RegexValidator(message='Le numéro de téléphone doit contenir 10 chiffres', regex='^\\d{9,10}$')], verbose_name='Numéro de téléphone de la personne joignable pendant le festival')),
                ('type_inscription', models.CharField(choices=[('0', 'Association'), ('1', 'Particulier'), ('2', 'Institution'), ('3', 'Entreprise'), ('4', 'autre')], default='0', max_length=10, verbose_name='Type de la structure')),
                ('date_inscription', models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscrition")),
                ('statut_exposant', models.CharField(choices=[('0', 'Inscription déposée'), ('1', 'Inscription incomplète ou en cours de validation'), ('5', 'Inscription valide mais en attente du cheque de caution'), ('2', 'Inscription validée'), ('3', 'Inscription refusée'), ('4', 'Inscription annulée')], default='0', max_length=10, verbose_name='Statut')),
            ],
        ),
    ]
