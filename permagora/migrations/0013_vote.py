# Generated by Django 2.2.27 on 2022-07-31 21:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('permagora', '0012_delete_vote'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_vote', models.CharField(choices=[(0, 'neutre'), (1, 'plus'), (2, 'moins')], default='0', max_length=10, verbose_name='type de commentaire')),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('proposition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='permagora.PropositionCharte')),
            ],
        ),
    ]
