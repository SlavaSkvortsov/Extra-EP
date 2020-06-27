import csv
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from typing import List, TextIO, Any, Dict

from django.utils.functional import cached_property
from django_registration.forms import User

from core.utils import parse_datetime_str
from extra_ep.models import Player, RaidRun, Boss, ConsumableUsage, Consumable, Report


class ReportImporter:
    def __init__(self, report_id: int, log_file: TextIO) -> None:
        self.report_id = report_id
        self.log_file = log_file

        # player_id: {consumable_id: ConsumableUsage}
        self._unfinished_consumables: Dict[int, Dict[int, ConsumableUsage]] = defaultdict(dict)

    def process(self) -> None:
        raid_run = None
        datetime_str = None

        for row in csv.reader(self.log_file):
            if raid_run is None:
                raid_run = self._create_unknown_raid()

            datetime_str, event = row[0].split('  ')

            if event == 'ENCOUNTER_START':
                if raid_run.begin is None:
                    raid_run.begin = parse_datetime_str(datetime_str)
                    raid_run.save()

                boss = Boss.objects.filter(encounter_id=int(row[1])).first()
                if boss is None:
                    continue

                if raid_run.raid_id is None:
                    raid_run.raid_id = boss.raid_id
                    raid_run.save()

                if raid_run.raid_id != boss.raid_id:
                    raid_run.end = parse_datetime_str(datetime_str)
                    raid_run.save()

                    raid_run = self._create_unknown_raid()
                    raid_run.raid_id = boss.raid_id
                    raid_run.save()

            elif event == 'UNIT_DIED':
                if raid_run.begin is None:
                    raid_run.begin = parse_datetime_str(datetime_str)
                    raid_run.save()

            elif event == 'ENCOUNTER_END':
                boss = Boss.objects.filter(encounter_id=int(row[1])).first()
                if boss is None:
                    continue

                time = parse_datetime_str(datetime_str)

                if boss.raid_end:
                    raid_run.end = time
                    raid_run.save()

                    self._finalize_current_run(time)
                    raid_run = None

            elif event == 'SPELL_AURA_APPLIED':
                self._make_consumable_usage(row, raid_run, parse_datetime_str(datetime_str))

            elif event == 'SPELL_AURA_REMOVED':
                self._finalize_consumable(row, parse_datetime_str(datetime_str))

        if raid_run:
            if raid_run.raid_id is not None:
                raid_run.end = parse_datetime_str(datetime_str)
                raid_run.save()
                self._finalize_current_run(parse_datetime_str(datetime_str))
            else:
                raid_run.delete()

    def _finalize_current_run(self, time: datetime):
        for consumables in self._unfinished_consumables.values():
            for cons_usage in consumables.values():
                cons_usage.end = time
                cons_usage.save()

        self._unfinished_consumables = defaultdict(dict)

    def _create_unknown_raid(self) -> RaidRun:
        return RaidRun.objects.create(
            report_id=self.report_id,
        )

    def _make_consumable_usage(self, row: List[Any], raid_run: RaidRun, time: datetime) -> None:
        consumable = self._all_consumables.get(int(row[9]))

        if consumable is None:
            return

        player = self._get_or_create_player(row[2])

        existing_unfinished_usage = self._unfinished_consumables[player.id].get(consumable.id)
        if existing_unfinished_usage is not None:
            existing_unfinished_usage.end = time
            existing_unfinished_usage.save()

        consumable_usage = ConsumableUsage(
            player=player,
            raid_run=raid_run,
            consumable=consumable,
            begin=time,
        )
        self._unfinished_consumables[player.id][consumable.id] = consumable_usage

    def _finalize_consumable(self, row: List[Any], time: datetime) -> None:
        consumable = self._all_consumables.get(int(row[9]))

        if consumable is None:
            return

        player = self._get_or_create_player(row[2])

        unfinished_usage = self._unfinished_consumables[player.id].get(consumable.id)
        if unfinished_usage is None:
            return

        unfinished_usage.end = time
        unfinished_usage.save()
        del self._unfinished_consumables[player.id][consumable.id]

    @lru_cache(maxsize=None)
    def _get_or_create_player(self, player_name: str) -> Player:
        if '-' in player_name:
            player_name, _ = player_name.split('-')

        player, _ = Player.objects.get_or_create(name=player_name)
        return player

    @cached_property
    def _all_consumables(self) -> Dict[int, Consumable]:
        return {consumable.spell_id: consumable for consumable in Consumable.objects.all()}
