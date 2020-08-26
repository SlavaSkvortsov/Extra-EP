# Generated by Django 3.1 on 2020-08-26 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extra_ep', '0015_auto_20200825_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumable',
            name='name',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='consumablegroup',
            name='consumables',
            field=models.ManyToManyField(to='extra_ep.Consumable', verbose_name='Расходники'),
        ),
        migrations.AlterField(
            model_name='consumablesset',
            name='consumables',
            field=models.ManyToManyField(blank=True, to='extra_ep.Consumable', verbose_name='Расходники'),
        ),
        migrations.AlterField(
            model_name='consumablesset',
            name='groups',
            field=models.ManyToManyField(blank=True, to='extra_ep.ConsumableGroup', verbose_name='Группы расходников'),
        ),
    ]