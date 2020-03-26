import csv
from datetime import date, datetime
from typing import List, TextIO, Set

from django.db.models import Count
from django.utils.functional import cached_property

from core.constants import ENCOUNTERS, ITEM_ID_TO_BONUS_EP, SPELL_TO_ITEM_MAP, TANKS, LIMITS
from core.utils import parse_datetime_str
from extra_ep.models import Combat, ItemConsumption, Player, Report


class ReportImporter:
    UNKNOWN_COMBAT_NAME = 'unknown_combat_name'

    def __init__(self, report_id: int, log_file: TextIO) -> None:
        self.report_id = report_id
        self.log_file = log_file

    def process(self) -> None:
        combat = self._create_unknown_combat()
        raids = set()

        for row in csv.reader(self.log_file):
            datetime_str, event = row[0].split('  ')

            if self._report.raid_day is None:
                self._report.raid_day = parse_datetime_str(datetime_str).date()
                self._report.save(update_fields=('raid_day',))

            if event == 'ENCOUNTER_START':
                time = parse_datetime_str(datetime_str)
                encounter = ENCOUNTERS[row[1]]
                raids.add(encounter.raid)
                if combat.encounter == self.UNKNOWN_COMBAT_NAME:
                    combat.encounter = encounter.boss_name
                    combat.started = time
                    combat.save()

                else:
                    combat = Combat.objects.create(
                        report_id=self.report_id,
                        encounter=encounter.boss_name,
                        started=time,
                        ended=time,
                    )
            elif event == 'ENCOUNTER_END' and combat:
                time = parse_datetime_str(datetime_str)
                combat.ended = time
                combat.save()
                combat = self._create_unknown_combat()
            elif event == 'SPELL_CAST_SUCCESS':
                self._make_item_consumption(row, combat)

        if combat and combat.encounter == self.UNKNOWN_COMBAT_NAME:
            combat.delete()

        self._report.raid_name = ', '.join(sorted(raids))
        self._report.save()
        self._post_analyze_report(raids)

    def _post_analyze_report(self, raids: Set[str]) -> None:
        limits = {}
        for raid in raids:
            new_limits = LIMITS.get(raid)
            if new_limits is None:
                continue

            for item_id, amount in new_limits.items():
                if item_id in limits:
                    limits[item_id] += amount
                else:
                    limits[item_id] = amount

        for item_id, amount in limits.items():
            qs = ItemConsumption.objects.filter(
                combat__report_id=self.report_id,
                item_id=item_id,
            ).order_by().values(
                'player_id',
            ).annotate(
                amount=Count('item_id'),
            ).filter(
                amount__gt=amount,
            ).values_list(
                'player_id', 'amount',
            )

            for player_id, total_amount in qs:
                item_consumptions_qs = ItemConsumption.objects.filter(
                    combat__report_id=self.report_id,
                    player_id=player_id,
                    item_id=item_id,
                ).order_by('-id')[:total_amount - amount]
                for item_consumption in item_consumptions_qs:
                    item_consumption.ep = 0
                    item_consumption.save()

    def _create_unknown_combat(self) -> Combat:
        return Combat.objects.create(
            report_id=self.report_id,
            encounter=self.UNKNOWN_COMBAT_NAME,
            started=datetime.now(),
            ended=datetime.now(),
        )

    @classmethod
    def _make_item_consumption(cls, row: List[str], combat: Combat) -> None:
        player_name = row[2]
        if not player_name.endswith('-РокДелар'):
            return

        spell_id = int(row[9])
        item_id = SPELL_TO_ITEM_MAP.get(spell_id)

        if item_id is None:
            return

        datetime_str, event = row[0].split('  ')
        time = parse_datetime_str(datetime_str)
        player_name = player_name[:-len('-РокДелар')]
        bonus_ep = cls._get_item_bonus_ep(item_id, player_name)
        player, _ = Player.objects.get_or_create(name=player_name)
        ItemConsumption.objects.create(
            combat_id=combat.id,
            player=player,
            spell_id=spell_id,
            item_id=item_id,
            ep=bonus_ep,
            used_at=time,
        )

    @staticmethod
    def _get_item_bonus_ep(item_id, player_name) -> int:
        if item_id == 13510 and player_name in TANKS:
            return 0

        return ITEM_ID_TO_BONUS_EP[item_id]

    @cached_property
    def _report(self) -> Report:
        return Report.objects.get(id=self.report_id)
