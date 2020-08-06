# Generated by Django 2.2.10 on 2020-08-05 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extra_ep', '0009_auto_20200713_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumablesset',
            name='consumables',
            field=models.ManyToManyField(blank=True, to='extra_ep.Consumable'),
        ),
        migrations.AlterField(
            model_name='consumablesset',
            name='groups',
            field=models.ManyToManyField(blank=True, to='extra_ep.ConsumableGroup'),
        ),
        migrations.CreateModel(
            name='ConsumableUsageLimit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('limit', models.IntegerField(verbose_name='Сколько за рейд можно съесть')),
                ('consumable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.Consumable')),
                ('raid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.Raid')),
            ],
            options={
                'ordering': ('-id',),
                'abstract': False,
            },
        ),
    ]
