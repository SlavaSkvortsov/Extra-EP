# Generated by Django 3.1 on 2020-09-06 10:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extra_ep', '0021_auto_20200905_0956'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumablegroup',
            name='image_url',
        ),
    ]