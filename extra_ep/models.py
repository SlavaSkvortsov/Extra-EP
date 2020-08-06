from datetime import timedelta

from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлено', auto_now=True)

    class Meta:
        ordering = ('-id',)
        abstract = True


class Boss(BaseModel):
    name = models.CharField(max_length=30)
    encounter_id = models.IntegerField(unique=True, verbose_name='ID боя. Гуглите encounter id')
    raid = models.ForeignKey('extra_ep.Raid', on_delete=models.CASCADE)
    raid_end = models.BooleanField(verbose_name='Конец рейда', default=False)

    def __str__(self):
        return self.name


class Raid(BaseModel):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Player(BaseModel):
    name = models.CharField(null=False, max_length=30, unique=True)
    role = models.ForeignKey('extra_ep.Role', on_delete=models.SET_NULL, null=True)
    klass = models.ForeignKey('extra_ep.Class', on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return self.name


class Role(BaseModel):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Class(BaseModel):
    name = models.CharField(max_length=30)
    color = models.CharField(verbose_name='Цвет (hex RGB)', max_length=6)

    def __str__(self):
        return self.name


class ConsumablesSet(BaseModel):
    role = models.ForeignKey('extra_ep.Role', on_delete=models.CASCADE)
    klass = models.ForeignKey('extra_ep.Class', on_delete=models.CASCADE)

    # TODO raid could be added here

    consumables = models.ManyToManyField('extra_ep.Consumable', blank=True)
    groups = models.ManyToManyField('extra_ep.ConsumableGroup', blank=True)

    class Meta:
        unique_together = ('role', 'klass')

    def __str__(self):
        return f'{self.klass} - {self.role}'


class Consumable(BaseModel):
    spell_id = models.IntegerField(verbose_name='ID заклинания', unique=True)
    item_id = models.IntegerField(verbose_name='ID предмета', unique=True)

    name = models.CharField(max_length=30, null=True, blank=True)

    points_for_usage = models.BooleanField(
        verbose_name='Давать очки за применение (без учета времени)',
        default=False,
    )

    points = models.IntegerField(verbose_name='Очки')

    def __str__(self):
        return self.name or 'Укажи, бля, имя, а то хуйня какая-то'


class ConsumableUsageLimit(BaseModel):
    consumable = models.ForeignKey('extra_ep.Consumable', on_delete=models.CASCADE)
    raid = models.ForeignKey('extra_ep.Raid', on_delete=models.CASCADE)

    limit = models.IntegerField(verbose_name='Сколько за рейд можно съесть')


class ConsumableGroup(BaseModel):
    name = models.CharField(verbose_name='Имя группы', max_length=30)
    points = models.IntegerField(verbose_name='Очки')
    consumables = models.ManyToManyField('extra_ep.Consumable')

    def __str__(self):
        return self.name


class RaidRun(BaseModel):
    report = models.ForeignKey('extra_ep.Report', on_delete=models.CASCADE)
    raid = models.ForeignKey('extra_ep.Raid', on_delete=models.SET_NULL, null=True)
    begin = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)

    required_uptime = models.FloatField(default=0.85)
    minimum_uptime = models.FloatField(default=0.5)
    points_coefficient = models.FloatField(default=1)

    active = models.BooleanField(default=True)

    def __str__(self):
        return f'Забег в {self.raid} {self.begin.date().isoformat()}'

    @property
    def duration(self) -> timedelta:
        return self.end - self.begin


class ConsumableUsage(BaseModel):
    raid_run = models.ForeignKey('extra_ep.RaidRun', on_delete=models.CASCADE)
    player = models.ForeignKey('extra_ep.Player', on_delete=models.CASCADE)

    consumable = models.ForeignKey('extra_ep.Consumable', on_delete=models.CASCADE)

    begin = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return f'{self.player} съел {self.consumable} в {self.raid_run.raid}'


class Report(BaseModel):
    uploaded_by = models.ForeignKey('auth.User', verbose_name='Загрузил', on_delete=models.CASCADE)
    static = models.IntegerField(
        verbose_name='Статик',
        default=1,
        choices=((1, 'Первый'), (2, 'Второй'), (3, 'Третий')),
        null=False,
    )
    raid_day = models.DateField(verbose_name='День рейда', null=True)
    raid_name = models.CharField(verbose_name='Рейд', max_length=200, null=True)
    flushed = models.BooleanField(verbose_name='Очки начислены', default=False)


class Combat(BaseModel):
    report = models.ForeignKey('extra_ep.Report', verbose_name='Отчет', on_delete=models.CASCADE)
    started = models.DateTimeField(verbose_name='Начало', null=False)
    ended = models.DateTimeField(verbose_name='Окончание', null=False)

    encounter = models.CharField(verbose_name='Бой', null=False, max_length=200)

    def __str__(self) -> str:
        return self.encounter


class ItemConsumption(BaseModel):
    combat = models.ForeignKey('extra_ep.Combat', verbose_name='Бой', on_delete=models.CASCADE)
    player = models.ForeignKey('extra_ep.Player', verbose_name='Игрок', on_delete=models.CASCADE)
    spell_id = models.IntegerField(null=False)
    item_id = models.IntegerField(null=False)
    used_at = models.DateTimeField(null=False, verbose_name='Применено')

    ep = models.IntegerField(null=False, verbose_name='EP')
