# Generated by Django 2.2.13 on 2020-09-26 21:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0037_auto_20200917_1223'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvenementAcceuil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name="Titre de l'événement (si laissé vide, ce sera le titre de l'article)")),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now, help_text='jj/mm/année', verbose_name='Date')),
                ('article', models.ForeignKey(help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)", on_delete=django.db.models.deletion.CASCADE, to='blog.Article')),
            ],
            options={
                'unique_together': {('article', 'start_time')},
            },
        ),
    ]