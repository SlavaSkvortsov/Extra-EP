from django.db import models


class Player(models.Model):
    name = models.CharField(null=False, max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name


class Report(models.Model):
    uploaded_by = models.ForeignKey('auth.User', verbose_name='Загрузил', on_delete=models.CASCADE)
    static = models.IntegerField(verbose_name='Статик', default=1, choices=((1, 'Первый'), (2, 'Второй')), null=False)
    raid_day = models.DateField(verbose_name='День рейда', null=True)
    raid_name = models.CharField(verbose_name='Рейд', max_length=200, null=True)
    flushed = models.BooleanField(verbose_name='Очки начислены', default=False)

    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлено', auto_now=True)


class Combat(models.Model):
    report = models.ForeignKey('extra_ep.Report', verbose_name='Отчет', on_delete=models.CASCADE)
    started = models.DateTimeField(verbose_name='Начало', null=False)
    ended = models.DateTimeField(verbose_name='Окончание', null=False)

    encounter = models.CharField(verbose_name='Бой', null=False, max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.encounter


class ItemConsumption(models.Model):
    combat = models.ForeignKey('extra_ep.Combat', verbose_name='Бой', on_delete=models.CASCADE)
    player = models.ForeignKey('extra_ep.Player', verbose_name='Игрок', on_delete=models.CASCADE)
    spell_id = models.IntegerField(null=False)
    item_id = models.IntegerField(null=False)
    used_at = models.DateTimeField(null=False, verbose_name='Применено')

    ep = models.IntegerField(null=False, verbose_name='EP')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
