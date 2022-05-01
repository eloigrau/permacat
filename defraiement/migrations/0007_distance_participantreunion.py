# Generated by Django 2.2.27 on 2022-05-01 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('defraiement', '0006_auto_20220209_1453'),
    ]

    operations = [
        migrations.CreateModel(
            name='Distance_ParticipantReunion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.TextField(blank=True, null=True, verbose_name='Distance calculée')),
                ('participant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='defraiement.ParticipantReunion')),
                ('reunion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='defraiement.Reunion')),
            ],
        ),
    ]