# Generated by Django 2.2.8 on 2020-02-17 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0027_auto_20200122_2125'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evenement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.TextField()),
                ('start_time', models.DateTimeField(blank=True, help_text='jj/mm/année', null=True, verbose_name='Date de début ')),
                ('end_time', models.DateTimeField(blank=True, help_text='jj/mm/année', null=True, verbose_name='Date de fin')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Article')),
            ],
        ),
    ]
