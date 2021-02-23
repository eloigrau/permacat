# Generated by Django 2.2.13 on 2020-08-25 20:27

from django.db import migrations, models
import django.db.models.deletion

def combine_names(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    article = apps.get_model('jardinpartage', 'Article')
    assos = apps.get_model('bourseLibre', 'Asso')
    asso_public, created = assos.objects.get_or_create(nom='Public')
    asso_permacat, created = assos.objects.get_or_create(nom='Permacat')


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0033_auto_20200825_2014'),
        ('vote', '0006_auto_20200820_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='suffrage',
            name='asso',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bourseLibre.Asso'),
        ),
        migrations.RunPython(combine_names, ),
    ]
