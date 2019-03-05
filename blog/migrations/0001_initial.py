# Generated by Django 2.1.7 on 2019-03-05 23:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categorie', models.CharField(choices=[('Agenda', 'Agenda'), ('Jardinage', 'Jardinage'), ('Recette', 'Recette'), ('Histoire', 'Histoire'), ('Bricolage', 'Bricolage'), ('Culture', 'Culture'), ('Bon_plan', 'Bon plan'), ('Point', 'Point de vue'), ('autre', 'autre')], default='Jardinage', max_length=30, verbose_name='categorie')),
                ('titre', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('contenu', models.TextField(null=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date de parution')),
            ],
            options={
                'ordering': ('date',),
            },
        ),
        migrations.CreateModel(
            name='Commentaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=42)),
                ('commentaire', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Article')),
            ],
        ),
    ]