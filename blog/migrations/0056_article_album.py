# Generated by Django 2.2.24 on 2021-06-19 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0025_auto_20210615_1409'),
        ('blog', '0055_auto_20210615_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='album',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='photologue.Album'),
        ),
    ]