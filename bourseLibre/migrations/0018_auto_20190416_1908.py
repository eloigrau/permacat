# Generated by Django 2.1.3 on 2019-04-16 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0017_auto_20190412_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produit',
            name='unite_prix',
            field=models.CharField(choices=[('don', 'don'), ('troc', 'troc'), ('pret', 'prêt'), ('G1', 'G1'), ('Soudaqui', 'Soudaqui'), ('SEL', 'SEL'), ('JEU', 'JEU'), ('heuresT', 'heuresT'), ('Autre', 'A négocier')], default='lliure', max_length=8, verbose_name='monnaie'),
        ),
    ]
