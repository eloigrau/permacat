# Generated by Django 2.2.28 on 2022-11-27 19:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0096_auto_20221127_2056'),
        ('vote', '0002_auto_20220803_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='suffrage',
            name='article',
            field=models.ForeignKey(blank=True, help_text='Article associé', null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.Article'),
        ),
    ]
