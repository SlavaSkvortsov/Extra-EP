from collections import namedtuple
from typing import Dict

Encounter = namedtuple('Encounter', ['boss_name', 'raid'])


class Raid:
    MC = 'Огненные Недра'
    ONYXIA = 'Логово Ониксии'
    BWL = 'Логово Крыла Тьмы'


ENCOUNTERS: Dict[str, Encounter] = {
    '663': Encounter(boss_name='Люцифрон', raid=Raid.MC),
    '664': Encounter(boss_name='Магмадар', raid=Raid.MC),
    '665': Encounter(boss_name='Гееннас', raid=Raid.MC),
    '666': Encounter(boss_name='Гарр', raid=Raid.MC),
    '667': Encounter(boss_name='Шаззрах', raid=Raid.MC),
    '668': Encounter(boss_name='Барон Геддон', raid=Raid.MC),
    '669': Encounter(boss_name='Предвестник Сульфурон', raid=Raid.MC),
    '670': Encounter(boss_name='Маг-лорд из клана Гордок', raid=Raid.MC),
    '671': Encounter(boss_name='Мажордом Экзекутус', raid=Raid.MC),
    '672': Encounter(boss_name='Рагнарос', raid=Raid.MC),

    '1084': Encounter(boss_name='Ониксия', raid=Raid.ONYXIA),

    '610': Encounter(boss_name='Бритвосмерт Неукротимый', raid=Raid.BWL),
    '611': Encounter(boss_name='Валестраз Порочный', raid=Raid.BWL),
    '612': Encounter(boss_name='Предводитель драконов Разящий Бич', raid=Raid.BWL),
    '613': Encounter(boss_name='Огнечрев', raid=Raid.BWL),
    '614': Encounter(boss_name='Черноскал', raid=Raid.BWL),
    '615': Encounter(boss_name='Пламегор', raid=Raid.BWL),
    '616': Encounter(boss_name='Хроммагус', raid=Raid.BWL),
    '617': Encounter(boss_name='Нефариан', raid=Raid.BWL),
}

SPELL_TO_ITEM_MAP = {
    27869: 20520,
    16666: 12662,
    17531: 13444,
    17530: 13443,
    17543: 13457,
    7233: 6049,
    11364: 9036,
    6615: 5634,
    11359: 9030,
    3169: 3387,
    17540: 13455,
    17534: 13446,
    9512: 7676,
    17528: 13442,
    17548: 13459,
    22756: 18262,
    17628: 13512,
    17626: 13510,
    17627: 13511,
    7242: 6048,
}

ITEM_ID_TO_BONUS_EP = {
    20520: 40,
    12662: 40,
    13444: 40,
    13443: 20,
    13457: 60,  # ГФПП
    13459: 60,  # ГШПП
    6048: 30,  # маленькое ШПП
    6049: 30,
    9036: 20,
    5634: 30,
    9030: 40,
    3387: 20,
    13455: 40,
    13446: 20,
    7676: 40,
    13442: 40,
    18262: 100,  # точильный каменень стихий
    13510: 1500,  # титанка ХП
    13511: 1500,  # титанка мана
    13512: 1500,  # титанка СПД
}

LIMITS = {
    Raid.MC: {
        13510: 0,  # титанка ХП
        13511: 1,  # титанка мана
        13512: 1,  # титанка СПД

        18262: 8,  # точильный каменень стихий
    },
    Raid.ONYXIA: {
        13510: 0,  # титанка ХП
        13511: 0,  # титанка мана
        13512: 0,  # титанка СПД

        18262: 2,  # точильный каменень стихий
    },
    Raid.BWL: {
        18262: 12,  # точильный каменень стихий

        13510: 1,  # титанка ХП
        13511: 1,  # титанка мана
        13512: 1,  # титанка СПД
    },
}

TANKS = {
    'Граф',
    'Аитера',
    'Охик',
    'Арахис',

    'Туморроу',
    'Лизон',
    'Атриккс',
}
