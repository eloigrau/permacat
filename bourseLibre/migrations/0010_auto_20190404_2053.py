# Generated by Django 2.1.3 on 2019-04-04 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0009_auto_20190403_2121'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='conversation',
            options={'ordering': ('-date_dernierMessage',)},
        ),
        migrations.AlterField(
            model_name='produit',
            name='unite_prix',
            field=models.CharField(choices=[('don', 'don'), ('troc', 'troc'), ('pret', 'pret'), ('G1', 'G1'), ('soudaqui', 'soudaqui'), ('SEL', 'SEL'), ('JEU', 'JEU'), ('heuresT', 'heuresT'), ('Autre', 'A negocier')], default='lliure', max_length=8, verbose_name='monnaie'),
        ),
    ]
