# Generated by Django 2.2.10 on 2020-08-08 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extra_ep', '0010_auto_20200805_2153'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='boss',
            options={'verbose_name': 'Босс', 'verbose_name_plural': 'Боссы'},
        ),
        migrations.AlterModelOptions(
            name='class',
            options={'verbose_name': 'Класс', 'verbose_name_plural': 'Классы'},
        ),
        migrations.AlterModelOptions(
            name='consumable',
            options={'verbose_name': 'Расходник', 'verbose_name_plural': 'Расходники'},
        ),
        migrations.AlterModelOptions(
            name='consumablegroup',
            options={'verbose_name': 'Группа расходников', 'verbose_name_plural': 'Группы расходников'},
        ),
        migrations.AlterModelOptions(
            name='consumablesset',
            options={'verbose_name': 'Набор расходников', 'verbose_name_plural': 'Наборы расходников'},
        ),
        migrations.AlterModelOptions(
            name='consumableusage',
            options={'verbose_name': 'Использование расходника', 'verbose_name_plural': 'Использование расходников'},
        ),
        migrations.AlterModelOptions(
            name='consumableusagelimit',
            options={'verbose_name': 'Лимит расходника', 'verbose_name_plural': 'Лимиты расходников'},
        ),
        migrations.AlterModelOptions(
            name='player',
            options={'verbose_name': 'Игрок', 'verbose_name_plural': 'Игроки'},
        ),
        migrations.AlterModelOptions(
            name='raid',
            options={'verbose_name': 'Рейд', 'verbose_name_plural': 'Рейды'},
        ),
        migrations.AlterModelOptions(
            name='raidrun',
            options={'verbose_name': 'Поход в рейд', 'verbose_name_plural': 'Походы в рейды'},
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ['-id'], 'verbose_name': 'Отчет', 'verbose_name_plural': 'Отчеты'},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'verbose_name': 'Роль', 'verbose_name_plural': 'Роли'},
        ),
        migrations.RenameField(
            model_name='consumable',
            old_name='points_for_usage',
            new_name='time_based_item',
        ),
        migrations.AddField(
            model_name='consumable',
            name='required',
            field=models.BooleanField(blank=True, default=True, verbose_name='Требуется'),
        ),
        migrations.AddField(
            model_name='consumablegroup',
            name='required',
            field=models.BooleanField(blank=True, default=True, verbose_name='Требуется'),
        ),
        migrations.AlterField(
            model_name='boss',
            name='raid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.Raid', verbose_name='Рейд'),
        ),
        migrations.AlterField(
            model_name='consumablesset',
            name='klass',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.Class', verbose_name='Класс'),
        ),
        migrations.AlterField(
            model_name='consumablesset',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.Role', verbose_name='Роль'),
        ),
        migrations.AlterField(
            model_name='consumableusage',
            name='consumable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.Consumable', verbose_name='Расходник'),
        ),
        migrations.AlterField(
            model_name='consumableusage',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.Player', verbose_name='Игрок'),
        ),
        migrations.AlterField(
            model_name='consumableusage',
            name='raid_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.RaidRun', verbose_name='Поход в рейд'),
        ),
        migrations.AlterField(
            model_name='consumableusagelimit',
            name='consumable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.Consumable', verbose_name='Расходник'),
        ),
        migrations.AlterField(
            model_name='consumableusagelimit',
            name='raid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.Raid', verbose_name='Рейд'),
        ),
        migrations.AlterField(
            model_name='player',
            name='klass',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='extra_ep.Class', verbose_name='Класс'),
        ),
        migrations.AlterField(
            model_name='player',
            name='role',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='extra_ep.Role', verbose_name='Роль'),
        ),
        migrations.AlterField(
            model_name='raidrun',
            name='raid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='extra_ep.Raid', verbose_name='Рейд'),
        ),
        migrations.AlterField(
            model_name='raidrun',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extra_ep.Report', verbose_name='Отчет'),
        ),
    ]