# Generated by Django 2.2.10 on 2020-02-28 16:40

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('extra_ep', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemconsumption',
            name='used_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 2, 28, 16, 40, 3, 392040, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
