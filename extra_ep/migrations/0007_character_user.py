# Generated by Django 2.2.10 on 2020-03-30 16:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('extra_ep', '0006_auto_20200330_1837'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Аккаунт'),
        ),
    ]
