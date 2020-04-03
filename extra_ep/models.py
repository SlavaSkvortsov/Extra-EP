from django.db import models

from core.constants import Raid


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлено', auto_now=True)

    class Meta:
        ordering = ('-id',)
        abstract = True


class Character(BaseModel):
    CLASS_DRUID = 'druid'
    CLASS_HUNTER = 'hunter'
    CLASS_MAGE = 'mage'
    CLASS_PALADIN = 'paladin'
    CLASS_PRIEST = 'priest'
    CLASS_ROGUE = 'rogue'
    # CLASS_SHAMAN = 'shaman'  not yet
    CLASS_WARLOCK = 'warlock'
    CLASS_WARRIOR = 'warrior'
    CLASS_UNKNOWN = 'unknown'

    CLASS_CHOICES = (
        (CLASS_UNKNOWN, 'Неизвестно'),
        (CLASS_DRUID, 'Друид'),
        (CLASS_HUNTER, 'Охотник'),
        (CLASS_MAGE, 'Маг'),
        (CLASS_PALADIN, 'Паладин'),
        (CLASS_PRIEST, 'Жрец'),
        (CLASS_ROGUE, 'Разбойник'),
        # (CLASS_SHAMAN, 'Шаман'),
        (CLASS_WARLOCK, 'Чернокнижник'),
        (CLASS_WARRIOR, 'Воин'),
    )

    name = models.CharField(null=False, verbose_name='Персонаж', max_length=30, unique=True)
    klass = models.CharField(
        null=False,
        verbose_name='Класс',
        max_length=20,
        default=CLASS_UNKNOWN,
        choices=CLASS_CHOICES,
    )
    user = models.ForeignKey('auth.User', null=True, verbose_name='Аккаунт', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Report(BaseModel):
    uploaded_by = models.ForeignKey('auth.User', verbose_name='Загрузил', on_delete=models.CASCADE)
    static = models.IntegerField(verbose_name='Статик', default=1, choices=((1, 'Первый'), (2, 'Второй')), null=False)
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
    character = models.ForeignKey('extra_ep.Character', verbose_name='Игрок', on_delete=models.CASCADE)
    spell_id = models.IntegerField(null=False)
    item_id = models.IntegerField(null=False)
    used_at = models.DateTimeField(null=False, verbose_name='Применено')

    ep = models.IntegerField(null=False, verbose_name='EP')


class RaidTemplate(BaseModel):
    name = models.CharField(max_length=200, verbose_name='Название')
    is_base_template = models.BooleanField(default=False)

    raid_leader = models.ForeignKey(
        'extra_ep.Character', on_delete=models.CASCADE, verbose_name='РЛ', related_name='+',
    )

    tanks = models.ManyToManyField(
        'extra_ep.Character', verbose_name='Танки', related_name='+', blank=True,
    )
    max_tanks = models.IntegerField(verbose_name='Максисум танков')

    healers = models.ManyToManyField(
        'extra_ep.Character', verbose_name='Хилы', related_name='+', blank=True,
    )
    max_healers = models.IntegerField(verbose_name='Максисум хилов')

    damage_dealers = models.ManyToManyField(
        'extra_ep.Character', verbose_name='ДД', related_name='+', blank=True,
    )
    max_damage_dealers = models.IntegerField(verbose_name='Максисум ДД')

    max_total = models.IntegerField(verbose_name='Максисум игроков в рейде')


class RaidEvent(BaseModel):
    event = models.OneToOneField('calendarium.Event', on_delete=models.CASCADE)

    raid = models.CharField(
        max_length=10,
        choices=(('mc', Raid.MC), ('bwl', Raid.BWL), ('zg', 'ЗулГурруб')),
        verbose_name='Рейд',
    )
    template = models.ForeignKey('extra_ep.RaidTemplate', on_delete=models.CASCADE)
