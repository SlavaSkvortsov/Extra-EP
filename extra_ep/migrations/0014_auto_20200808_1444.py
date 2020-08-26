# Generated by Django 2.2.10 on 2020-08-08 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extra_ep', '0013_auto_20200808_1426'),
    ]

    operations = [
        migrations.RenameField(
            model_name='consumable',
            old_name='time_based_item',
            new_name='usage_based_item',
        ),
        migrations.AlterField(
            model_name='consumable',
            name='required',
            field=models.BooleanField(blank=True, default=True, verbose_name='Требуется (влияет только на очки за время)'),
        ),
    ]