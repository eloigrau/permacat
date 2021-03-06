# Generated by Django 2.1.3 on 2019-04-12 10:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0016_auto_20190409_2034'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageGeneralPermacat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='produit_service',
            name='souscategorie',
            field=models.CharField(choices=[('jardinage', 'jardinage'), ('éducation', 'éducation'), ('santé', 'santé'), ('bricolage', 'bricolage'), ('informatique', 'informatique'), ('hebergement', 'hebergement'), ('cuisine', 'cuisine'), ('batiment', 'batiment'), ('mécanique', 'mécanique'), ('autre', 'autre')], default='j', max_length=20),
        ),
        migrations.AddField(
            model_name='profil',
            name='cotisation_a_jour',
            field=models.BooleanField(default=False, verbose_name='Cotisation à jour'),
        ),
    ]
