# Generated by Django 3.1 on 2020-10-04 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extra_ep', '0024_auto_20200913_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumable',
            name='broken',
            field=models.BooleanField(default=False, verbose_name='Не отображается в логах'),
        ),
    ]
