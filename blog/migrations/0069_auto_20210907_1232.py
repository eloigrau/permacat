# Generated by Django 2.2.24 on 2021-09-07 10:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0068_discussion_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='slug',
            field=models.SlugField(default=uuid.uuid4, max_length=100),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='titre',
            field=models.CharField(max_length=32, verbose_name='Titre de la discussion'),
        ),
        migrations.AlterUniqueTogether(
            name='discussion',
            unique_together={('article', 'slug')},
        ),
    ]