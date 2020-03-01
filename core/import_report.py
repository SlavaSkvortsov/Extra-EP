import csv
from typing import List, TextIO

from django.utils.functional import cached_property

from core.constants import ENCOUNTERS, ITEM_ID_TO_BONUS_EP, SPELL_TO_ITEM_MAP
from core.utils import parse_datetime_str
from extra_ep.models import Combat, ItemConsumption, Player, Report


class ReportImporter:
    def __init__(self, report_id: int, log_file: TextIO) -> None:
        self.report_id = report_id
        self.log_file = log_file

    def process(self) -> None:
        combat = None
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
                combat = None
            elif combat and event == 'SPELL_CAST_SUCCESS':
                self._make_item_consumption(row, combat)

        self._report.raid_name = ', '.join(sorted(raids))

    @staticmethod
    def _make_item_consumption(row: List[str], combat: Combat) -> None:
        player_name = row[2]
        if not player_name.endswith('-РокДелар'):
            return

        spell_id = int(row[9])
        item_id = SPELL_TO_ITEM_MAP.get(spell_id)

        if item_id is None:
            return

        datetime_str, event = row[0].split('  ')
        time = parse_datetime_str(datetime_str)
        bonus_ep = ITEM_ID_TO_BONUS_EP[item_id]
        player_name = player_name[:-len('-РокДелар')]
        player, _ = Player.objects.get_or_create(name=player_name)
        ItemConsumption.objects.create(
            combat_id=combat.id,
            player=player,
            spell_id=spell_id,
            item_id=item_id,
            ep=bonus_ep,
            used_at=time,
        )

    @cached_property
    def _report(self) -> Report:
        return Report.objects.get(id=self.report_id)
