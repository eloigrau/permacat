# Generated by Django 2.2.24 on 2021-07-29 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0049_auto_20210729_1553'),
        ('blog', '0061_auto_20210727_2059'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdresseArticle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Nom du lieu')),
                ('adresse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bourseLibre.Adresse')),
                ('article', models.ForeignKey(help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)", on_delete=django.db.models.deletion.CASCADE, to='blog.Article')),
            ],
        ),
    ]
