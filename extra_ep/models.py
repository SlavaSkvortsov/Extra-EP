from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлено', auto_now=True)

    class Meta:
        ordering = ('-id',)
        abstract = True


class Boss(BaseModel):
    name = models.CharField(verbose_name='Имя', max_length=30)
    encounter_id = models.IntegerField(unique=True, verbose_name='ID боя. Гуглите encounter id')
    raid = models.ForeignKey('extra_ep.Raid', verbose_name='Рейд', on_delete=models.CASCADE)
    raid_end = models.BooleanField(verbose_name='Конец рейда', default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Босс'
        verbose_name_plural = 'Боссы'


class Raid(BaseModel):
    name = models.CharField(verbose_name='Название', max_length=30)

    default_required_uptime = models.FloatField(verbose_name='Необходимый аптайм по умолчанию', default=0.85)
    default_minimum_uptime = models.FloatField(verbose_name='Минимальный аптайм по умолчанию', default=0.5)
    default_points_coefficient = models.FloatField(verbose_name='Коэффициент очков по времени по умолчанию', default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рейд'
        verbose_name_plural = 'Рейды'


class Player(BaseModel):
    name = models.CharField(verbose_name='Имя', null=False, max_length=30, unique=True)
    role = models.ForeignKey('extra_ep.Role', verbose_name='Роль', on_delete=models.SET_NULL, null=True)
    klass = models.ForeignKey('extra_ep.Class', verbose_name='Класс', on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'


class Role(BaseModel):
    name = models.CharField(verbose_name='Имя', max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


class Class(BaseModel):
    name = models.CharField(verbose_name='Имя', max_length=30)
    color = models.CharField(verbose_name='Цвет (hex RGB)', max_length=6)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'


class ConsumablesSet(BaseModel):
    role = models.ForeignKey('extra_ep.Role', verbose_name='Роль', on_delete=models.CASCADE)
    klass = models.ForeignKey('extra_ep.Class', verbose_name='Класс', on_delete=models.CASCADE)

    # TODO raid could be added here

    consumables = models.ManyToManyField('extra_ep.Consumable', blank=True, verbose_name='Расходники')
    groups = models.ManyToManyField('extra_ep.ConsumableGroup', blank=True, verbose_name='Группы расходников')

    class Meta:
        unique_together = ('role', 'klass')
        verbose_name = 'Набор расходников'
        verbose_name_plural = 'Наборы расходников'

    def __str__(self):
        return f'{self.klass} - {self.role}'


class Consumable(BaseModel):
    spell_id = models.IntegerField(verbose_name='ID заклинания')
    item_id = models.IntegerField(verbose_name='ID предмета', null=True, blank=True)

    name = models.CharField(verbose_name='Имя', max_length=30, null=True, blank=True)

    usage_based_item = models.BooleanField(
        verbose_name='Давать очки за использование, а не за время',
        default=False,
    )

    points_for_usage = models.IntegerField(verbose_name='Очки за одно использование', blank=False, null=False)
    points_over_raid = models.IntegerField(verbose_name='Очки за рейд', blank=True, null=True)
    required = models.BooleanField(verbose_name='Требуется (влияет только на очки за время)', blank=True, default=True)

    def __str__(self):
        return self.name or 'Укажи, бля, имя, а то хуйня какая-то'

    def clean(self):
        if not self.usage_based_item and self.points_over_raid is None:
            raise ValidationError(
                'Необходимо указать очки за рейд или поставить галочку "Давать очки за использование"',
            )

        return super().clean()

    class Meta:
        verbose_name = 'Расходник'
        verbose_name_plural = 'Расходники'


class ConsumableUsageLimit(BaseModel):
    consumable = models.ForeignKey('extra_ep.Consumable', verbose_name='Расходник', on_delete=models.CASCADE)
    raid = models.ForeignKey('extra_ep.Raid', verbose_name='Рейд', on_delete=models.CASCADE)

    limit = models.IntegerField(verbose_name='Сколько за рейд можно съесть')

    class Meta:
        verbose_name = 'Лимит расходника'
        verbose_name_plural = 'Лимиты расходников'


class ConsumableGroup(BaseModel):
    name = models.CharField(verbose_name='Имя группы', max_length=30)
    points = models.IntegerField(verbose_name='Очки')
    consumables = models.ManyToManyField('extra_ep.Consumable', verbose_name='Расходники')
    required = models.BooleanField(verbose_name='Требуется', blank=True, default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа расходников'
        verbose_name_plural = 'Группы расходников'


class RaidRun(BaseModel):
    report = models.ForeignKey('extra_ep.Report', verbose_name='Отчет', on_delete=models.CASCADE)
    raid = models.ForeignKey('extra_ep.Raid', verbose_name='Рейд', on_delete=models.SET_NULL, null=True)
    begin = models.DateTimeField(verbose_name='Начало', null=True)
    end = models.DateTimeField(verbose_name='Окончание', null=True)

    required_uptime = models.FloatField(verbose_name='Необходимый аптайм', default=0.85)
    minimum_uptime = models.FloatField(verbose_name='Минимальный аптайм', default=0.5)
    points_coefficient = models.FloatField(verbose_name='Коэффициент очков по времени', default=1)

    def __str__(self):
        return f'Забег в {self.raid} {self.begin and self.begin.date().isoformat()}'

    @property
    def duration(self) -> timedelta:
        return self.end - self.begin

    class Meta:
        verbose_name = 'Поход в рейд'
        verbose_name_plural = 'Походы в рейды'


class ConsumableUsage(BaseModel):
    raid_run = models.ForeignKey('extra_ep.RaidRun', verbose_name='Поход в рейд', on_delete=models.CASCADE)
    player = models.ForeignKey('extra_ep.Player', verbose_name='Игрок', on_delete=models.CASCADE)

    consumable = models.ForeignKey('extra_ep.Consumable', verbose_name='Расходник', on_delete=models.CASCADE)

    begin = models.DateTimeField(verbose_name='Начало действия')
    end = models.DateTimeField(verbose_name='Окончание действия')

    def __str__(self):
        return f'{self.player} съел {self.consumable} в {self.raid_run.raid}'

    class Meta:
        verbose_name = 'Использование расходника'
        verbose_name_plural = 'Использование расходников'


class Report(BaseModel):
    uploaded_by = models.ForeignKey('auth.User', verbose_name='Загрузил', on_delete=models.CASCADE)
    static = models.IntegerField(
        verbose_name='Статик',
        default=2,
        choices=((2, 'Второй'), (3, 'Третий'), (1, 'Первый :(')),
        null=False,
    )
    raid_day = models.DateField(verbose_name='День рейда', null=True)
    raid_name = models.CharField(verbose_name='Рейд', max_length=200, null=True)
    flushed = models.BooleanField(verbose_name='Очки начислены', default=False)
    is_hard_mode = models.BooleanField(verbose_name='Режим освоения, очки за использование', default=False)

    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.raid_name} ({self.raid_day})'


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
